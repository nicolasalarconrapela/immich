<script lang="ts">
  import AssetLightbox from '$lib/components/calendar-page/asset-lightbox.svelte';
  import CalendarControls from '$lib/components/calendar-page/calendar-controls.svelte';
  import CalendarGrid from '$lib/components/calendar-page/calendar-grid.svelte';
  import DayDetailPanel from '$lib/components/calendar-page/day-detail-panel.svelte';
  import DayView from '$lib/components/calendar-page/day-view.svelte';
  import WeekView from '$lib/components/calendar-page/week-view.svelte';
  import YearView from '$lib/components/calendar-page/year-view.svelte';
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

  // Viewer State (Lightbox)
  let viewedAsset: AssetResponseDto | null = $state(null);
  let lightboxAssets: AssetResponseDto[] = $state([]);

  // assetsByDay needs to be updated to match the type expected by CalendarGrid
  // CalendarGrid expects: assetsByDay: Map<string, { count: number; assets: AssetResponseDto[] }>
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
    if (viewMode === 'month' || viewMode === '2weeks') {
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

  // Go to month view for a specific month
  function goToMonthView(date: DateTime) {
    currentDate = date;
    viewMode = 'month';
    loadMonthData();
  }

  // Close day panel
  function closePanel() {
    selectedDay = null;
    selectedAssets = [];
  }

  // Jump to specific date
  function jumpToDate(date: DateTime) {
    currentDate = date;
  }

  // Lightbox functions
  function openLightbox(asset: AssetResponseDto, context: AssetResponseDto[] = []) {
    viewedAsset = asset;
    // Ensure the current asset is in the context if not empty, otherwise default to just this one
    if (context.length > 0) {
      lightboxAssets = context;
    } else {
      lightboxAssets = [asset];
    }
  }

  function closeLightbox() {
    viewedAsset = null;
    lightboxAssets = [];
  }

  function navigateLightbox(direction: number) {
    if (!viewedAsset || lightboxAssets.length === 0) return;

    const currentIndex = lightboxAssets.findIndex((a) => a.id === viewedAsset?.id);
    if (currentIndex === -1) return;

    const newIndex = currentIndex + direction;

    if (newIndex >= 0 && newIndex < lightboxAssets.length) {
      viewedAsset = lightboxAssets[newIndex];
    }
  }

  // Basic toggle selection for demo purposes
  function toggleSelection(asset: AssetResponseDto) {
    const index = selectedAssets.findIndex((a) => a.id === asset.id);
    if (index >= 0) {
      selectedAssets = selectedAssets.filter((a) => a.id !== asset.id);
    } else {
      selectedAssets = [...selectedAssets, asset];
    }
  }

  // Load data on mount
  $effect(() => {
    if (viewMode === 'month' || viewMode === '2weeks') {
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
      onJumpToDate={jumpToDate}
      bind:viewMode
    />
  {/snippet}

  <div class="calendar-wrapper">
    {#if viewMode === 'day'}
      <DayView {currentDate} onNavigate={navigate} />
    {:else if viewMode === 'week'}
      <WeekView {currentDate} onNavigate={navigate} onDaySelect={goToDayView} onAssetClick={openLightbox} />
    {:else if viewMode === 'year'}
      <YearView {currentDate} onNavigate={navigate} onMonthSelect={goToMonthView} onDaySelect={goToDayView} />
    {:else if viewMode === 'month'}
      <CalendarGrid {currentDate} {assetsByDay} {isLoading} onDayClick={selectDay} />

      {#if selectedDay && selectedAssets.length > 0}
        <DayDetailPanel date={selectedDay} assets={selectedAssets} onClose={closePanel} />
      {/if}
    {:else}
      <!-- Placeholder for other views -->
      <div class="coming-soon">
        <p>Vista "{viewMode}" próximamente...</p>
        <p class="hint">Por ahora, usa Día, Semana, Mes o Año</p>
      </div>
    {/if}
  </div>

  <!-- Quick Lightbox Overlay -->
  {#if viewedAsset}
    <AssetLightbox
      asset={viewedAsset}
      onClose={closeLightbox}
      onToggleSelect={toggleSelection}
      isSelected={selectedAssets.some((a) => a.id === viewedAsset?.id)}
      onNext={lightboxAssets.length > 1 &&
      lightboxAssets.findIndex((a) => a.id === viewedAsset?.id) < lightboxAssets.length - 1
        ? () => navigateLightbox(1)
        : undefined}
      onPrevious={lightboxAssets.length > 1 && lightboxAssets.findIndex((a) => a.id === viewedAsset?.id) > 0
        ? () => navigateLightbox(-1)
        : undefined}
    />
  {/if}
</UserPageLayout>

<style>
  .calendar-wrapper {
    height: 100%;
    width: 100%;
    background: #0a0a0a;
    overflow-y: auto;
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
