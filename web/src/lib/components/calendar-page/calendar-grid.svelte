<script lang="ts">
  import type { AssetResponseDto } from '@immich/sdk';
  import { AssetMediaSize } from '@immich/sdk';
  import { Icon } from '@immich/ui';
  import { mdiCamera, mdiLoading } from '@mdi/js';
  import { DateTime } from 'luxon';

  interface DayData {
    date: DateTime;
    isCurrentMonth: boolean;
    assetCount: number;
    thumbnails: string[];
    tags: Array<{ name: string; color: string }>;
  }

  interface Props {
    currentDate: DateTime;
    assetsByDay: Map<string, { count: number; assets: AssetResponseDto[] }>;
    isLoading: boolean;
    onDayClick: (day: DateTime, assets: AssetResponseDto[]) => void;
  }

  let { currentDate, assetsByDay, isLoading, onDayClick }: Props = $props();

  // Get weekday names (short, starting Monday)
  const weekDays = ['lun', 'mar', 'mié', 'jue', 'vie', 'sáb', 'dom'];

  // Get days for the calendar grid
  const calendarDays = $derived.by(() => {
    const days: DayData[] = [];

    const startOfMonth = currentDate.startOf('month');
    const endOfMonth = currentDate.endOf('month');

    // Get the first day of the calendar (may be in previous month)
    const startOfCalendar = startOfMonth.startOf('week');
    const endOfCalendar = endOfMonth.endOf('week');

    let current = startOfCalendar;
    while (current <= endOfCalendar) {
      const dayKey = current.toISODate() ?? '';
      const dayData = assetsByDay.get(dayKey);

      // Get first 4 thumbnails for preview
      const thumbnails: string[] = [];
      const tags: Array<{ name: string; color: string }> = [];

      if (dayData && dayData.assets) {
        for (const asset of dayData.assets.slice(0, 4)) {
          thumbnails.push(`/api/assets/${asset.id}/thumbnail?size=${AssetMediaSize.Thumbnail}`);

          // Collect unique tags
          for (const tag of asset.tags || []) {
            if (!tags.find((t) => t.name === tag.value)) {
              tags.push({
                name: tag.value || tag.name || '',
                color: tag.color || '#4ade80',
              });
            }
          }
        }
      }

      days.push({
        date: current,
        isCurrentMonth: current.month === currentDate.month,
        assetCount: dayData?.count ?? 0,
        thumbnails,
        tags: tags.slice(0, 2), // Max 2 tags visible
      });
      current = current.plus({ days: 1 });
    }

    return days;
  });

  const today = DateTime.now().toISODate();
</script>

<div class="calendar-container">
  <!-- Weekday headers -->
  <div class="weekday-header">
    {#each weekDays as day}
      <div class="weekday">{day}</div>
    {/each}
  </div>

  <!-- Calendar grid -->
  {#if isLoading}
    <div class="loading-container">
      <Icon icon={mdiLoading} size="48" class="animate-spin" />
    </div>
  {:else}
    <div class="calendar-grid">
      {#each calendarDays as day}
        {@const isToday = day.date.toISODate() === today}
        {@const hasAssets = day.assetCount > 0}
        {@const showThumbnails = day.assetCount > 0 && day.thumbnails.length > 0}

        <button
          type="button"
          class="day-cell"
          class:other-month={!day.isCurrentMonth}
          class:today={isToday}
          class:has-assets={hasAssets}
          onclick={() => hasAssets && onDayClick(day.date, assetsByDay.get(day.date.toISODate() ?? '')?.assets || [])}
          disabled={!hasAssets}
        >
          <!-- Day number -->
          <div class="day-header">
            <span class="day-number" class:today-number={isToday}>
              {day.date.day}
            </span>
            {#if hasAssets && !showThumbnails}
              <span class="dot"></span>
            {/if}
          </div>

          <!-- Tags -->
          {#if day.tags.length > 0 && !showThumbnails}
            <div class="day-tags">
              {#each day.tags as tag}
                <span class="tag-pill" style="background-color: {tag.color}; color: white;">
                  {tag.name.slice(0, 10)}
                </span>
              {/each}
            </div>
          {/if}

          <!-- Thumbnails grid -->
          {#if showThumbnails}
            <div class="thumbnails-grid">
              {#each day.thumbnails.slice(0, 4) as thumb, i}
                <div class="thumb-wrapper">
                  <img src={thumb} alt="" loading="lazy" />
                  {#if i === 3 && day.assetCount > 4}
                    <div class="thumb-overlay">
                      <Icon icon={mdiCamera} size="12" />
                      <span>{day.assetCount}</span>
                    </div>
                  {/if}
                </div>
              {/each}
            </div>
          {/if}
        </button>
      {/each}
    </div>
  {/if}
</div>

<style>
  .calendar-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    padding: 0.5rem;
    background: var(--immich-bg);
  }

  .weekday-header {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 2px;
    margin-bottom: 0.5rem;
  }

  .weekday {
    text-align: center;
    font-size: 0.75rem;
    font-weight: 500;
    color: #f97316;
    padding: 0.5rem 0;
    text-transform: lowercase;
  }

  .loading-container {
    display: flex;
    align-items: center;
    justify-content: center;
    flex: 1;
    color: var(--immich-primary);
  }

  .calendar-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 2px;
    flex: 1;
  }

  .day-cell {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    padding: 4px;
    background: #1a1a1a;
    border: none;
    border-radius: 4px;
    min-height: 80px;
    cursor: default;
    transition: all 0.2s ease;
  }

  .day-cell.has-assets {
    cursor: pointer;
  }

  .day-cell.has-assets:hover {
    background: #2a2a2a;
    transform: scale(1.02);
  }

  .day-cell.other-month {
    opacity: 0.4;
  }

  .day-header {
    display: flex;
    align-items: center;
    gap: 4px;
    width: 100%;
  }

  .day-number {
    font-size: 0.875rem;
    font-weight: 500;
    color: #e5e5e5;
  }

  .today-number {
    background: #22c55e;
    color: white;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
  }

  .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #f97316;
  }

  .day-tags {
    display: flex;
    flex-direction: column;
    gap: 2px;
    margin-top: 4px;
    width: 100%;
    overflow: hidden;
  }

  .tag-pill {
    font-size: 0.6rem;
    padding: 2px 6px;
    border-radius: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
  }

  .thumbnails-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 2px;
    margin-top: 4px;
    width: 100%;
    flex: 1;
  }

  .thumb-wrapper {
    position: relative;
    aspect-ratio: 1;
    border-radius: 4px;
    overflow: hidden;
  }

  .thumb-wrapper img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .thumb-overlay {
    position: absolute;
    inset: 0;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 2px;
    color: white;
    font-size: 0.7rem;
    font-weight: 600;
  }

  @media (max-width: 768px) {
    .day-cell {
      min-height: 60px;
      padding: 2px;
    }

    .day-number {
      font-size: 0.75rem;
    }

    .tag-pill {
      font-size: 0.5rem;
      padding: 1px 4px;
    }
  }
</style>
