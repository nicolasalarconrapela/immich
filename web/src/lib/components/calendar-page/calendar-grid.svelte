<script lang="ts">
  import { Icon } from '@immich/ui';
  import { mdiLoading } from '@mdi/js';
  import { DateTime, Info } from 'luxon';

  interface Props {
    currentDate: DateTime;
    assetsByDay: Map<string, number>;
    isLoading: boolean;
    onDayClick: (day: DateTime) => void;
  }

  let { currentDate, assetsByDay, isLoading, onDayClick }: Props = $props();

  // Get weekday names
  const weekDays = Info.weekdays('short');

  // Get days for the calendar grid
  const calendarDays = $derived.by(() => {
    const days: Array<{ date: DateTime; isCurrentMonth: boolean; assetCount: number }> = [];

    const startOfMonth = currentDate.startOf('month');
    const endOfMonth = currentDate.endOf('month');

    // Get the first day of the calendar (may be in previous month)
    const startOfCalendar = startOfMonth.startOf('week');
    const endOfCalendar = endOfMonth.endOf('week');

    let current = startOfCalendar;
    while (current <= endOfCalendar) {
      const dayKey = current.toISODate() ?? '';
      days.push({
        date: current,
        isCurrentMonth: current.month === currentDate.month,
        assetCount: assetsByDay.get(dayKey) ?? 0,
      });
      current = current.plus({ days: 1 });
    }

    return days;
  });

  const today = DateTime.now().toISODate();

  function getIntensity(count: number): string {
    if (count === 0) return '';
    if (count < 5) return 'bg-immich-primary/20 dark:bg-immich-dark-primary/20';
    if (count < 15) return 'bg-immich-primary/40 dark:bg-immich-dark-primary/40';
    if (count < 30) return 'bg-immich-primary/60 dark:bg-immich-dark-primary/60';
    return 'bg-immich-primary/80 dark:bg-immich-dark-primary/80';
  }
</script>

<div class="flex flex-col h-full p-4">
  <!-- Weekday headers -->
  <div class="grid grid-cols-7 gap-1 mb-2">
    {#each weekDays as day}
      <div class="text-center text-sm font-medium text-gray-500 dark:text-gray-400 py-2">
        {day}
      </div>
    {/each}
  </div>

  <!-- Calendar grid -->
  {#if isLoading}
    <div class="flex items-center justify-center flex-1">
      <Icon icon={mdiLoading} size="48" class="animate-spin text-immich-primary" />
    </div>
  {:else}
    <div class="grid grid-cols-7 gap-1 flex-1">
      {#each calendarDays as day}
        {@const isToday = day.date.toISODate() === today}
        {@const hasAssets = day.assetCount > 0}

        <button
          type="button"
          class="relative flex flex-col items-center justify-start p-2 rounded-lg transition-all
            {day.isCurrentMonth ? 'text-gray-900 dark:text-gray-100' : 'text-gray-400 dark:text-gray-600'}
            {isToday ? 'ring-2 ring-immich-primary dark:ring-immich-dark-primary' : ''}
            {getIntensity(day.assetCount)}
            {hasAssets ? 'hover:scale-105 hover:shadow-lg cursor-pointer' : 'cursor-default'}
            min-h-[80px] md:min-h-[100px]"
          onclick={() => hasAssets && onDayClick(day.date)}
          disabled={!hasAssets}
        >
          <!-- Day number -->
          <span
            class="text-sm md:text-base font-medium
              {isToday
              ? 'bg-immich-primary text-white rounded-full w-6 h-6 md:w-8 md:h-8 flex items-center justify-center'
              : ''}"
          >
            {day.date.day}
          </span>

          <!-- Asset count -->
          {#if hasAssets}
            <span class="mt-1 text-xs md:text-sm font-semibold text-immich-primary dark:text-immich-dark-primary">
              {day.assetCount}
              <span class="hidden md:inline">📷</span>
            </span>
          {/if}
        </button>
      {/each}
    </div>
  {/if}
</div>

<style>
  /* Ensure calendar takes full height */
  .grid.flex-1 {
    height: 0; /* Needed for proper flex behavior */
    min-height: 400px;
  }
</style>
