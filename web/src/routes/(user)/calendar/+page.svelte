<script lang="ts">
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import UserPageLayout from '$lib/components/layouts/user-page-layout.svelte';
  import CalendarGrid from '$lib/components/calendar-page/calendar-grid.svelte';
  import CalendarControls from '$lib/components/calendar-page/calendar-controls.svelte';
  import DayView from '$lib/components/calendar-page/day-view.svelte';
  import { searchAssets } from '@immich/sdk';
  import { t } from 'svelte-i18n';
  import { DateTime } from 'luxon';

  // Current viewing month/year
  let currentDate = $state(DateTime.now());

  // Selected day (null = month view, Date = day view)
  let selectedDay: DateTime | null = $state(null);

  // Assets grouped by day for the current month
  let assetsByDay: Map<string, number> = $state(new Map());

  // Loading state
  let isLoading = $state(true);

  // View mode
  let viewMode: 'month' | 'week' | 'day' = $state('month');

  // Load asset counts for the current month
  async function loadMonthData() {
    isLoading = true;

    const startOfMonth = currentDate.startOf('month');
    const endOfMonth = currentDate.endOf('month');

    try {
      const result = await searchAssets({
        metadataSearchDto: {
          takenAfter: startOfMonth.toISO() ?? undefined,
          takenBefore: endOfMonth.toISO() ?? undefined,
          size: 1000,
          withExif: false,
        }
      });

      // Group assets by day
      const dayMap = new Map<string, number>();

      for (const asset of result.assets.items) {
        const date = DateTime.fromISO(asset.fileCreatedAt);
        const dayKey = date.toISODate() ?? '';

        if (dayKey) {
          dayMap.set(dayKey, (dayMap.get(dayKey) ?? 0) + 1);
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
    loadMonthData();
  }

  // Navigate to today
  function goToToday() {
    currentDate = DateTime.now();
    selectedDay = null;
    loadMonthData();
  }

  // Select a day
  function selectDay(day: DateTime) {
    selectedDay = day;
  }

  // Go back to month view
  function backToMonth() {
    selectedDay = null;
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

  <div class="h-full w-full">
    {#if selectedDay}
      <DayView
        date={selectedDay}
        onBack={backToMonth}
      />
    {:else}
      <CalendarGrid
        {currentDate}
        {assetsByDay}
        {isLoading}
        onDayClick={selectDay}
      />
    {/if}
  </div>
</UserPageLayout>
