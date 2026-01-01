<script lang="ts">
  import type { AssetResponseDto } from '@immich/sdk';
  import { AssetMediaSize } from '@immich/sdk';
  import { Icon } from '@immich/ui';
  import { mdiLoading } from '@mdi/js';
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
    {#each weekDays as day (day)}
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
      {#each calendarDays as day (day.date.toISO())}
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
              <div class="dot-indicator">
                <span class="dot"></span>
                <span class="dot-count">{day.assetCount}</span>
              </div>
            {/if}
          </div>

          <!-- Tags -->
          {#if day.tags.length > 0 && !showThumbnails}
            <div class="day-tags">
              {#each day.tags as tag (tag.name)}
                <span class="tag-pill" style="--tag-color: {tag.color}">
                  {tag.name.slice(0, 10)}
                </span>
              {/each}
            </div>
          {/if}

          <!-- Thumbnails grid -->
          {#if showThumbnails}
            <div class="thumbnails-grid">
              {#each day.thumbnails.slice(0, 4) as thumb, i (thumb)}
                <div class="thumb-wrapper">
                  <img src={thumb} alt="" loading="lazy" />
                  {#if i === 3 && day.assetCount > 4}
                    <div class="thumb-overlay">
                      <span class="overlay-count">+{day.assetCount - 4}</span>
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
  :global(:root) {
    --cal-bg: #0f172a; /* Slate 900 */
    --cal-cell-bg: #1e293b; /* Slate 800 */
    --cal-cell-hover: #334155; /* Slate 700 */
    --cal-accent: #38bdf8; /* Sky 400 */
    --cal-text: #f8fafc; /* Slate 50 */
    --cal-text-muted: #94a3b8; /* Slate 400 */
  }

  .calendar-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    padding: 1rem;
    background: var(--cal-bg);
    color: var(--cal-text);
  }

  .weekday-header {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .weekday {
    text-align: center;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--cal-text-muted);
    padding: 0.5rem 0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .loading-container {
    display: flex;
    align-items: center;
    justify-content: center;
    flex: 1;
    color: var(--cal-accent);
  }

  .calendar-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    grid-auto-rows: minmax(100px, 1fr);
    gap: 0.5rem;
    flex: 1;
    overflow-y: auto;
  }

  .day-cell {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    padding: 0.5rem;
    background: var(--cal-cell-bg);
    border: 1px solid rgba(255, 255, 255, 0.03);
    border-radius: 0.75rem;
    position: relative;
    cursor: default;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
  }

  .day-cell.today {
    background: rgba(56, 189, 248, 0.1); /* Tinted background for today */
    border-color: rgba(56, 189, 248, 0.3);
  }

  .day-cell.has-assets {
    cursor: pointer;
  }

  .day-cell.has-assets:hover {
    background: var(--cal-cell-hover);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    border-color: rgba(255, 255, 255, 0.1);
  }

  .day-cell.other-month {
    opacity: 0.3;
    background: transparent;
    border-color: transparent;
  }

  .day-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    width: 100%;
    margin-bottom: 0.25rem;
  }

  .day-number {
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--cal-text);
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
  }

  .today-number {
    background: var(--cal-accent);
    color: #0f172a;
    box-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
  }

  .dot-indicator {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--cal-accent);
    box-shadow: 0 0 5px var(--cal-accent);
  }

  .dot-count {
    font-size: 0.7rem;
    color: var(--cal-text-muted);
  }

  .day-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-top: auto;
    width: 100%;
  }

  .tag-pill {
    font-size: 0.6rem;
    padding: 2px 6px;
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.1);
    color: var(--cal-text);
    border-left: 2px solid var(--tag-color);
  }

  /* Thumbnails */
  .thumbnails-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 2px;
    margin-top: 0.5rem;
    width: 100%;
    border-radius: 6px;
    overflow: hidden;
    flex: 1; /* occupy remaining space */
  }

  .thumb-wrapper {
    position: relative;
    width: 100%;
    aspect-ratio: 1;
    overflow: hidden;
  }

  .thumb-wrapper img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
  }

  .day-cell:hover .thumb-wrapper img {
    transform: scale(1.1);
  }

  .thumb-overlay {
    position: absolute;
    inset: 0;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    backdrop-filter: blur(2px);
  }

  .overlay-count {
    color: white;
    font-size: 0.75rem;
    font-weight: 700;
  }

  @media (max-width: 768px) {
    .calendar-container {
      padding: 0.5rem;
    }

    .calendar-grid {
      gap: 2px;
    }

    .day-cell {
      min-height: 80px;
      padding: 0.25rem;
      border-radius: 0.5rem;
    }

    .day-number {
      font-size: 0.8rem;
      width: 24px;
      height: 24px;
    }

    .tag-pill {
      display: none;
    }
  }
</style>
