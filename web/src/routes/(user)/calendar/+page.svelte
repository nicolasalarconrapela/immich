<script lang="ts">
  import CalendarControls from '$lib/components/calendar-page/calendar-controls.svelte';
  import CalendarGrid from '$lib/components/calendar-page/calendar-grid.svelte';
  import DayDetailPanel from '$lib/components/calendar-page/day-detail-panel.svelte';
  import DayView from '$lib/components/calendar-page/day-view.svelte';
  import WeekView from '$lib/components/calendar-page/week-view.svelte';
  import UserPageLayout from '$lib/components/layouts/user-page-layout.svelte';
  import type { AssetResponseDto } from '@immich/sdk';
  import { searchAssets } from '@immich/sdk';
  import { DateTime } from 'luxon';
  import { t } from 'svelte-i18n';

  // View mode type
  type ViewMode = 'day' | 'week' | '2weeks' | 'month' | 'year' | 'agenda';

  // Current viewing date
  let currentDate = $state(DateTime.now());

  // Selected day data (for month view panel)
  let selectedDay: DateTime | null = $state(null);
  let selectedAssets: AssetResponseDto[] = $state([]);

  // Assets grouped by day for the current month
  let assetsByDay: Map<string, { count: number; assets: AssetResponseDto[] }> = $state(new Map());

  // Loading state
  let isLoading = $state(true);

  // View mode
  let viewMode: ViewMode = $state('month');

  // Load assets for month/grid views
  async function loadMonthData() {
    isLoading = true;

    const startOfMonth = currentDate.startOf('month').startOf('week');
    const endOfMonth = currentDate.endOf('month').endOf('week');

    try {
      const result = await searchAssets({
        metadataSearchDto: {
          takenAfter: startOfMonth.toISO() ?? undefined,
          takenBefore: endOfMonth.toISO() ?? undefined,
          size: 1000,
          withExif: true,
          withPeople: true,
        },
      });

      // Group assets by day
      const dayMap = new Map<string, { count: number; assets: AssetResponseDto[] }>();

      for (const asset of result.assets.items) {
        const date = DateTime.fromISO(asset.fileCreatedAt);
        const dayKey = date.toISODate() ?? '';

        if (dayKey) {
          if (!dayMap.has(dayKey)) {
            dayMap.set(dayKey, { count: 0, assets: [] });
          }
          const dayData = dayMap.get(dayKey)!;
          dayData.count++;
          dayData.assets.push(asset);
        }
      }

      assetsByDay = dayMap;
    } catch (error) {
      console.error('Failed to load calendar data:', error);
    } finally {
      isLoading = false;
    }
  }

  // Navigate based on view mode
  function navigate(direction: number) {
    selectedDay = null;

    switch (viewMode) {
      case 'day':
        currentDate = currentDate.plus({ days: direction });
        break;
      case 'week':
        currentDate = currentDate.plus({ weeks: direction });
        break;
      case '2weeks':
        currentDate = currentDate.plus({ weeks: direction * 2 });
        loadMonthData();
        break;
      case 'month':
        currentDate = currentDate.plus({ months: direction });
        loadMonthData();
        break;
      case 'year':
        currentDate = currentDate.plus({ years: direction });
        loadMonthData();
        break;
      default:
        currentDate = currentDate.plus({ months: direction });
        loadMonthData();
    }
  }

  // Navigate to today
  function goToToday() {
    currentDate = DateTime.now();
    selectedDay = null;
    if (viewMode === 'month' || viewMode === '2weeks' || viewMode === 'year') {
      loadMonthData();
    }
  }

  // Select a day (from month/week view)
  function selectDay(day: DateTime, assets: AssetResponseDto[]) {
    selectedDay = day;
    selectedAssets = assets;
  }

  // Go to day view for a specific day
  function goToDayView(day: DateTime) {
    currentDate = day;
    viewMode = 'day';
    selectedDay = null;
  }

  // Close day panel
  function closePanel() {
    selectedDay = null;
    selectedAssets = [];
  }

  // Load data on mount and view change
  $effect(() => {
    if (viewMode === 'month' || viewMode === '2weeks' || viewMode === 'year') {
      loadMonthData();
    }
  });
</script>

<UserPageLayout title={$t('calendar')} showUploadButton>
  {#snippet buttons()}
    <CalendarControls
      {currentDate}
      onPrevious={() => navigate(-1)}
      onNext={() => navigate(1)}
      onToday={goToToday}
      bind:viewMode
    />
  {/snippet}

  <div class="calendar-wrapper">
    {#if viewMode === 'day'}
      <DayView {currentDate} onNavigate={navigate} />
    {:else if viewMode === 'week'}
      <WeekView {currentDate} onNavigate={navigate} onDaySelect={goToDayView} />
    {:else if viewMode === 'month'}
      <CalendarGrid {currentDate} {assetsByDay} {isLoading} onDayClick={selectDay} />

      {#if selectedDay && selectedAssets.length > 0}
        <DayDetailPanel date={selectedDay} assets={selectedAssets} onClose={closePanel} />
      {/if}
    {:else}
      <!-- Placeholder for other views -->
      <div class="coming-soon">
        <p>Vista "{viewMode}" próximamente...</p>
        <p class="hint">Por ahora, usa Día, Semana o Mes</p>
      </div>
    {/if}
  </div>
</UserPageLayout>

<style>
  .calendar-wrapper {
    height: 100%;
    width: 100%;
    background: #0a0a0a;
  }

  .coming-soon {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #666;
    font-size: 1.25rem;
  }

  .hint {
    font-size: 0.875rem;
    margin-top: 0.5rem;
    color: #444;
  }
</style>
