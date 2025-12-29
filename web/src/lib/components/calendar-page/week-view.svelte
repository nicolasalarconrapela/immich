<script lang="ts">
  import { Icon } from '@immich/ui';
  import { mdiCamera, mdiChevronLeft, mdiChevronRight, mdiLoading } from '@mdi/js';
  import { DateTime } from 'luxon';
  import { searchAssets, AssetMediaSize } from '@immich/sdk';
  import type { AssetResponseDto } from '@immich/sdk';
  import { goto } from '$app/navigation';
  import { AppRoute } from '$lib/constants';

  interface DayData {
    date: DateTime;
    isToday: boolean;
    assets: AssetResponseDto[];
  }

  interface Props {
    currentDate: DateTime;
    onNavigate: (direction: number) => void;
    onDaySelect: (date: DateTime) => void;
  }

  let { currentDate, onNavigate, onDaySelect }: Props = $props();

  let weekDays: DayData[] = $state([]);
  let isLoading = $state(true);

  // Week range
  const weekStart = $derived(currentDate.startOf('week'));
  const weekEnd = $derived(currentDate.endOf('week'));
  const weekLabel = $derived(`${weekStart.toFormat('d MMM')} - ${weekEnd.toFormat('d MMM yyyy')}`);

  // Total photos for the week
  const totalPhotos = $derived(weekDays.reduce((sum, day) => sum + day.assets.length, 0));

  // Load assets for the week
  async function loadWeekAssets() {
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

        days.push({
          date,
          isToday: date.hasSame(today, 'day'),
          assets: dayAssets,
        });
      }

      weekDays = days;
    } catch (error) {
      console.error('Failed to load week assets:', error);
    } finally {
      isLoading = false;
    }
  }

  function openAsset(assetId: string) {
    goto(`${AppRoute.PHOTOS}/${assetId}`);
  }

  // Reload when date changes
  $effect(() => {
    currentDate; // dependency
    loadWeekAssets();
  });
</script>

<div class="week-view">
  <!-- Week header -->
  <div class="week-header">
    <button type="button" class="nav-btn" onclick={() => onNavigate(-1)}>
      <Icon icon={mdiChevronLeft} size="24" />
    </button>

    <div class="week-info">
      <span class="week-label">{weekLabel}</span>
      {#if totalPhotos > 0}
        <span class="photo-count">
          <Icon icon={mdiCamera} size="14" />
          {totalPhotos} fotos
        </span>
      {/if}
    </div>

    <button type="button" class="nav-btn" onclick={() => onNavigate(1)}>
      <Icon icon={mdiChevronRight} size="24" />
    </button>
  </div>

  <!-- Week grid -->
  {#if isLoading}
    <div class="loading">
      <Icon icon={mdiLoading} size="48" class="animate-spin" />
    </div>
  {:else}
    <div class="week-grid">
      {#each weekDays as day}
        {@const hasAssets = day.assets.length > 0}

        <div class="day-column" class:has-assets={hasAssets} class:today={day.isToday}>
          <!-- Day header -->
          <button type="button" class="day-header" onclick={() => onDaySelect(day.date)}>
            <span class="day-name">{day.date.toFormat('ccc')}</span>
            <span class="day-number" class:today-number={day.isToday}>
              {day.date.day}
            </span>
            {#if hasAssets}
              <span class="day-count">{day.assets.length}</span>
            {/if}
          </button>

          <!-- Day content -->
          <div class="day-content">
            {#if hasAssets}
              <div class="assets-scroll">
                {#each day.assets.slice(0, 20) as asset, i}
                  <button type="button" class="asset-thumb" onclick={() => openAsset(asset.id)}>
                    <img
                      src={`/api/assets/${asset.id}/thumbnail?size=${AssetMediaSize.Thumbnail}`}
                      alt=""
                      loading="lazy"
                    />
                  </button>
                {/each}
                {#if day.assets.length > 20}
                  <div class="more-indicator">
                    +{day.assets.length - 20} más
                  </div>
                {/if}
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
  .week-view {
    height: 100%;
    display: flex;
    flex-direction: column;
    background: #0a0a0a;
  }

  .week-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem;
    border-bottom: 1px solid #222;
    position: sticky;
    top: 0;
    background: #0a0a0a;
    z-index: 10;
  }

  .nav-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    background: none;
    border: none;
    color: white;
    padding: 0.5rem;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: background 0.2s;
  }

  .nav-btn:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  .week-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
  }

  .week-label {
    font-size: 1.125rem;
    font-weight: 500;
    color: white;
    text-transform: capitalize;
  }

  .photo-count {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.75rem;
    color: #888;
  }

  .loading {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--immich-primary);
  }

  .week-grid {
    flex: 1;
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 1px;
    background: #222;
    overflow: hidden;
  }

  .day-column {
    display: flex;
    flex-direction: column;
    background: #0a0a0a;
    min-height: 0;
  }

  .day-column.today {
    background: #111;
  }

  .day-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
    padding: 0.75rem 0.5rem;
    background: none;
    border: none;
    border-bottom: 1px solid #222;
    cursor: pointer;
    transition: background 0.2s;
    width: 100%;
  }

  .day-header:hover {
    background: rgba(255, 255, 255, 0.05);
  }

  .day-name {
    font-size: 0.7rem;
    text-transform: uppercase;
    color: #666;
    font-weight: 500;
  }

  .today .day-name {
    color: #f97316;
  }

  .day-number {
    font-size: 1.25rem;
    font-weight: 500;
    color: white;
  }

  .today-number {
    background: #22c55e;
    color: white;
    border-radius: 50%;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.875rem;
  }

  .day-count {
    font-size: 0.65rem;
    color: #888;
    background: #222;
    padding: 0.125rem 0.375rem;
    border-radius: 0.25rem;
  }

  .has-assets .day-count {
    background: #f97316;
    color: white;
  }

  .day-content {
    flex: 1;
    overflow-y: auto;
    padding: 0.25rem;
  }

  .assets-scroll {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .asset-thumb {
    width: 100%;
    aspect-ratio: 1;
    border-radius: 4px;
    overflow: hidden;
    border: none;
    padding: 0;
    cursor: pointer;
    transition:
      transform 0.2s,
      opacity 0.2s;
  }

  .asset-thumb:hover {
    opacity: 0.8;
  }

  .asset-thumb img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .more-indicator {
    text-align: center;
    font-size: 0.7rem;
    color: #666;
    padding: 0.5rem;
  }

  .no-assets {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #333;
    font-size: 0.7rem;
  }

  /* Responsive: Stack columns on mobile */
  @media (max-width: 768px) {
    .week-grid {
      grid-template-columns: 1fr;
      overflow-y: auto;
    }

    .day-column {
      flex-direction: row;
      min-height: auto;
      border-bottom: 1px solid #222;
    }

    .day-header {
      flex-direction: row;
      gap: 0.75rem;
      width: auto;
      padding: 1rem;
      border-bottom: none;
      border-right: 1px solid #222;
    }

    .day-content {
      padding: 0.5rem;
    }

    .assets-scroll {
      flex-direction: row;
      flex-wrap: wrap;
      gap: 0.5rem;
    }

    .asset-thumb {
      width: 60px;
      height: 60px;
    }

    .no-assets {
      justify-content: flex-start;
      padding-left: 1rem;
    }
  }
</style>
