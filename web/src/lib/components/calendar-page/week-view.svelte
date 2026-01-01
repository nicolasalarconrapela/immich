<script lang="ts">
  import { goto } from '$app/navigation';
  import { AppRoute } from '$lib/constants';
  import type { AssetResponseDto } from '@immich/sdk';
  import { AssetMediaSize, searchAssets } from '@immich/sdk';
  import { Icon } from '@immich/ui';
  import { mdiLoading } from '@mdi/js';
  import { DateTime } from 'luxon';
  import { onDestroy } from 'svelte';

  interface DayData {
    date: DateTime;
    isToday: boolean;
    assets: AssetResponseDto[];
    assetsByHour: { hour: number; assets: AssetResponseDto[] }[];
  }

  interface Props {
    currentDate: DateTime;
    onNavigate: (direction: number) => void;
    onDaySelect: (date: DateTime) => void;
    onAssetClick?: (asset: AssetResponseDto, context: AssetResponseDto[]) => void;
  }

  let { currentDate, onNavigate: _, onDaySelect, onAssetClick }: Props = $props();

  let weekDays: DayData[] = $state([]);
  let isLoading = $state(true);

  // AbortController for cancelling pending requests
  let abortController: AbortController | null = null;

  // Week range
  const weekStart = $derived(currentDate.startOf('week'));
  const weekEnd = $derived(currentDate.endOf('week'));

  // Get weekday names (short, starting Monday)

  // Load assets for the week
  async function loadWeekAssets() {
    // Cancel any previous pending request
    if (abortController) {
      abortController.abort();
    }

    // Create new abort controller for this request
    abortController = new AbortController();
    const currentAbortController = abortController;

    isLoading = true;

    try {
      const result = await searchAssets({
        metadataSearchDto: {
          takenAfter: weekStart.toISO() ?? undefined,
          takenBefore: weekEnd.toISO() ?? undefined,
          size: 1000,
          withExif: true,
        },
      });

      // Check if this request was aborted while waiting
      if (currentAbortController.signal.aborted) {
        return;
      }

      // Group by day
      const today = DateTime.now();
      const days: DayData[] = [];

      for (let i = 0; i < 7; i++) {
        const date = weekStart.plus({ days: i });
        const dayKey = date.toISODate();
        const dayAssets = result.assets.items.filter((a) => {
          const assetDate = DateTime.fromISO(a.fileCreatedAt).toISODate();
          return assetDate === dayKey;
        });

        // Group assets by hour for this day
        // Group assets by hour for this day
        const hourlyGroups: Record<number, AssetResponseDto[]> = {};
        for (const asset of dayAssets) {
          const hour = DateTime.fromISO(asset.fileCreatedAt).hour;
          if (!hourlyGroups[hour]) {
            hourlyGroups[hour] = [];
          }
          hourlyGroups[hour].push(asset);
        }

        const hourlyData = Object.entries(hourlyGroups)
          .map(([hour, assets]) => ({ hour: Number.parseInt(hour), assets }))
          .sort((a, b) => a.hour - b.hour);

        days.push({
          date,
          isToday: date.hasSame(today, 'day'),
          assets: dayAssets,
          assetsByHour: hourlyData,
        });
      }

      weekDays = days;
    } catch (error) {
      // Ignore abort errors
      if (error instanceof Error && error.name === 'AbortError') {
        return;
      }
      console.error('Failed to load week assets:', error);
    } finally {
      // Only set loading to false if this is still the active request
      if (!currentAbortController.signal.aborted) {
        isLoading = false;
      }
    }
  }

  function openAsset(asset: AssetResponseDto, context: AssetResponseDto[]) {
    if (onAssetClick) {
      onAssetClick(asset, context);
    } else {
      void goto(`${AppRoute.PHOTOS}/${asset.id}`);
    }
  }

  // Cleanup on unmount
  onDestroy(() => {
    if (abortController) {
      abortController.abort();
    }
  });

  // Reload when date changes
  $effect(() => {
    // track currentDate changes
    ((_) => {})(currentDate);
    void loadWeekAssets();
  });
</script>

<div class="week-view">
  <!-- Week grid -->
  {#if isLoading}
    <div class="loading">
      <Icon icon={mdiLoading} size="48" class="animate-spin" />
    </div>
  {:else}
    <div class="week-grid">
      {#each weekDays as day (day.date.toISO())}
        {@const hasAssets = day.assets.length > 0}

        <div class="day-column" class:today={day.isToday}>
          <!-- Day header -->
          <button type="button" class="day-header" onclick={() => onDaySelect(day.date)}>
            <span class="day-name" class:today-text={day.isToday}>{day.date.toFormat('ccc')}</span>
            <div class="number-wrapper" class:today-circle={day.isToday}>
              <span class="day-number">{day.date.day}</span>
            </div>

            <div class="indicators">
              {#if hasAssets}
                <div class="dot dot-blue"></div>
                {#if day.assets.length > 5}
                  <div class="dot dot-orange"></div>
                {/if}
                {#if day.assets.length > 15}
                  <div class="dot dot-teal"></div>
                {/if}
              {/if}
            </div>
          </button>

          <!-- Day content -->
          <div class="day-content">
            {#if hasAssets}
              <div class="hourly-groups">
                {#each day.assetsByHour as group (group.hour)}
                  <div class="hour-cluster">
                    <div class="hour-timestamp">{group.hour}:00</div>
                    <div class="assets-grid">
                      {#each group.assets as asset (asset.id)}
                        <button type="button" class="asset-thumb" onclick={() => openAsset(asset, day.assets)}>
                          <img
                            src={`/api/assets/${asset.id}/thumbnail?size=${AssetMediaSize.Thumbnail}`}
                            alt=""
                            loading="lazy"
                          />
                        </button>
                      {/each}
                    </div>
                  </div>
                {/each}
              </div>
            {:else}
              <div class="no-assets">
                <span>Sin fotos</span>
              </div>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  :global(:root) {
    --bg-main: #0f172a;
    --bg-card: #1e293b;
    --border-color: #334155;
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
    --accent: #38bdf8;
  }

  .week-view {
    height: 100%;
    display: flex;
    flex-direction: column;
    background: #000000;
    color: #ffffff;
  }

  .loading {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #00f2ff;
  }

  .week-grid {
    flex: 1;
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    background: #111111;
    gap: 1px;
    overflow-y: auto;
  }

  .day-column {
    display: flex;
    flex-direction: column;
    background: #000000;
    min-height: 0;
    position: relative;
  }

  .day-column.today {
    background: #0a0a0a;
  }

  .day-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1rem 0;
    background: none;
    border: none;
    cursor: pointer;
    width: 100%;
    gap: 0.75rem;
    transition: background 0.2s;
  }

  .day-header:hover {
    background: #0f0f0f;
  }

  .day-name {
    font-size: 0.75rem;
    font-weight: 600;
    color: #666666;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .today-text {
    color: #00f2ff; /* Vibrant Cyan */
    font-weight: 700;
  }

  .number-wrapper {
    width: 42px;
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: all 0.2s;
  }

  .today-circle {
    background: #00f2ff;
    box-shadow: 0 0 15px rgba(0, 242, 255, 0.4);
  }

  .day-number {
    font-size: 1.5rem;
    font-weight: 500;
    color: #ffffff;
    line-height: 1;
  }

  .today-circle .day-number {
    color: #000000;
    font-weight: 700;
  }

  .indicators {
    display: flex;
    gap: 0.25rem;
    height: 6px;
    align-items: center;
    justify-content: center;
  }

  .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
  }

  .dot-blue {
    background: #3b82f6;
  }
  .dot-orange {
    background: #f59e0b;
  }
  .dot-teal {
    background: #14b8a6;
  }

  .day-content {
    flex: 1;
    overflow-y: auto;
    padding: 0.5rem;
    scrollbar-width: thin;
    scrollbar-color: #334155 transparent;
  }

  .hourly-groups {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .hour-cluster {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .hour-timestamp {
    font-size: 0.65rem;
    font-weight: 700;
    color: #444;
    text-transform: uppercase;
    border-bottom: 1px solid #111;
    padding-bottom: 2px;
    margin-bottom: 2px;
  }

  .assets-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(45%, 1fr));
    gap: 4px;
  }

  .asset-thumb {
    width: 100%;
    aspect-ratio: 1;
    border-radius: 4px;
    overflow: hidden;
    border: none;
    padding: 0;
    cursor: pointer;
    transition: transform 0.2s;
    background: #000;
  }

  .asset-thumb:hover {
    transform: scale(1.05);
    z-index: 10;
  }

  .asset-thumb img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }

  .no-assets {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #222;
    font-size: 0.75rem;
    font-style: italic;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .week-grid {
      grid-template-columns: 1fr;
      gap: 0; /* No vertical lines on mobile list */
    }

    .day-column {
      flex-direction: row;
      border-bottom: 1px solid var(--border-color);
    }

    .day-header {
      flex-direction: row;
      gap: 1rem;
      width: 80px; /* Fixed width sidebar on mobile */
      padding: 1rem 0.5rem;
      border-bottom: none;
      border-right: 1px solid var(--border-color);
      justify-content: center;
    }

    .day-content {
      padding: 0.75rem;
    }

    .asset-thumb {
      width: 64px;
      height: 64px;
    }

    .no-assets {
      justify-content: flex-start;
      padding-left: 0.5rem;
    }
  }
</style>
