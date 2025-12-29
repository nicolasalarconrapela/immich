<script lang="ts">
  import CalendarControls from '$lib/components/calendar-page/calendar-controls.svelte';
  import CalendarGrid from '$lib/components/calendar-page/calendar-grid.svelte';
  import DayDetailPanel from '$lib/components/calendar-page/day-detail-panel.svelte';
  import UserPageLayout from '$lib/components/layouts/user-page-layout.svelte';
  import type { AssetResponseDto } from '@immich/sdk';
  import { searchAssets } from '@immich/sdk';
  import { DateTime } from 'luxon';
  import { t } from 'svelte-i18n';

  // Current viewing month/year
  let currentDate = $state(DateTime.now());

  // Selected day data
  let selectedDay: DateTime | null = $state(null);
  let selectedAssets: AssetResponseDto[] = $state([]);

  // Assets grouped by day for the current month
  let assetsByDay: Map<string, { count: number; assets: AssetResponseDto[] }> = $state(new Map());

  // Loading state
  let isLoading = $state(true);

  // View mode
  let viewMode: 'month' | 'week' | 'day' = $state('month');

  // Load asset counts for the current month
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

  // Navigate to previous/next month
  function navigateMonth(direction: number) {
    currentDate = currentDate.plus({ months: direction });
    selectedDay = null;
    loadMonthData();
  }

  // Navigate to today
  function goToToday() {
    currentDate = DateTime.now();
    selectedDay = null;
    loadMonthData();
  }

  // Select a day
  function selectDay(day: DateTime, assets: AssetResponseDto[]) {
    selectedDay = day;
    selectedAssets = assets;
  }

  // Close day panel
  function closePanel() {
    selectedDay = null;
    selectedAssets = [];
  }

  // Initial load
  $effect(() => {
    loadMonthData();
  });
</script>

<UserPageLayout title={$t('calendar')} showUploadButton>
  {#snippet buttons()}
    <CalendarControls
      {currentDate}
      onPrevious={() => navigateMonth(-1)}
      onNext={() => navigateMonth(1)}
      onToday={goToToday}
      bind:viewMode
    />
  {/snippet}

  <div class="calendar-wrapper">
    <CalendarGrid {currentDate} {assetsByDay} {isLoading} onDayClick={selectDay} />

    {#if selectedDay && selectedAssets.length > 0}
      <DayDetailPanel date={selectedDay} assets={selectedAssets} onClose={closePanel} />
    {/if}
  </div>
</UserPageLayout>

<style>
  .calendar-wrapper {
    height: 100%;
    width: 100%;
    background: #0a0a0a;
  }
</style>
