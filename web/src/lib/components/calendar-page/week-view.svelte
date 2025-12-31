<script lang="ts">
  import { goto } from '$app/navigation';
  import { AppRoute } from '$lib/constants';
  import type { AssetResponseDto } from '@immich/sdk';
  import { AssetMediaSize, searchAssets } from '@immich/sdk';
  import { Icon } from '@immich/ui';
  import { mdiCamera, mdiChevronLeft, mdiChevronRight, mdiLoading } from '@mdi/js';
  import { DateTime } from 'luxon';

  interface DayData {
    date: DateTime;
    isToday: boolean;
    assets: AssetResponseDto[];
  }

  interface Props {
    currentDate: DateTime;
    onNavigate: (direction: number) => void;
    onDaySelect: (date: DateTime) => void;
    onAssetClick?: (asset: AssetResponseDto, context: AssetResponseDto[]) => void;
  }

  let { currentDate, onNavigate, onDaySelect, onAssetClick }: Props = $props();

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

  function openAsset(asset: AssetResponseDto, context: AssetResponseDto[]) {
    if (onAssetClick) {
      onAssetClick(asset, context);
    } else {
      goto(`${AppRoute.PHOTOS}/${asset.id}`);
    }
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
                  <button type="button" class="asset-thumb" onclick={() => openAsset(asset, day.assets)}>
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
    background: var(--bg-main);
    color: var(--text-main);
  }

  .week-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 2rem;
    background: rgba(15, 23, 42, 0.95);
    backdrop-filter: blur(8px);
    border-bottom: 1px solid var(--border-color);
    position: sticky;
    top: 0;
    z-index: 10;
  }

  .nav-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.05);
    border: none;
    color: var(--text-main);
    padding: 0.5rem;
    border-radius: 50%;
    cursor: pointer;
    transition: all 0.2s;
  }

  .nav-btn:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: scale(1.1);
  }

  .week-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
  }

  .week-label {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-main);
    text-transform: capitalize;
  }

  .photo-count {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.8rem;
    color: var(--text-muted);
    font-weight: 500;
  }

  .loading {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--accent);
  }

  .week-grid {
    flex: 1;
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 1px; /* Gap for borders */
    background: var(--border-color); /* Lines color */
    overflow-y: auto;
    overflow-x: hidden;
  }

  .day-column {
    display: flex;
    flex-direction: column;
    background: var(--bg-main);
    min-height: 0;
  }

  .day-column.today {
    background: rgba(56, 189, 248, 0.05); /* Very subtle accent tint */
  }

  .day-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
    padding: 1rem 0.5rem;
    background: none;
    border: none;
    border-bottom: 1px solid var(--border-color);
    cursor: pointer;
    transition: background 0.2s;
    width: 100%;
  }

  .day-header:hover {
    background: rgba(255, 255, 255, 0.03);
  }

  .day-name {
    font-size: 0.75rem;
    text-transform: uppercase;
    color: var(--text-muted);
    font-weight: 600;
    letter-spacing: 0.05em;
  }

  .today .day-name {
    color: var(--accent);
  }

  .day-number {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text-main);
    line-height: 1;
  }

  .today-number {
    color: var(--accent);
  }

  .day-count {
    font-size: 0.7rem;
    color: var(--text-muted);
    background: rgba(255, 255, 255, 0.05);
    padding: 0.15rem 0.5rem;
    border-radius: 1rem;
    font-weight: 500;
    margin-top: 0.25rem;
  }

  .has-assets .day-count {
    background: rgba(56, 189, 248, 0.15);
    color: var(--accent);
  }

  .day-content {
    flex: 1;
    overflow-y: auto;
    padding: 0.5rem;
    /* Custom Scrollbar */
    scrollbar-width: thin;
    scrollbar-color: var(--border-color) transparent;
  }

  .assets-scroll {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .asset-thumb {
    width: 100%;
    aspect-ratio: 1;
    border-radius: 0.5rem;
    overflow: hidden;
    border: none;
    padding: 0;
    cursor: pointer;
    transition:
      transform 0.2s,
      opacity 0.2s;
    background: #000;
    position: relative;
  }

  .asset-thumb:hover {
    transform: scale(1.02);
    z-index: 2;
  }

  .asset-thumb img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }

  .more-indicator {
    text-align: center;
    font-size: 0.75rem;
    color: var(--text-muted);
    padding: 0.5rem;
  }

  .no-assets {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: rgba(255, 255, 255, 0.1);
    font-size: 0.8rem;
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

    .day-header .day-count {
      display: none; /* Hide count in sidebar to save space */
    }

    .day-content {
      padding: 0.75rem;
    }

    .assets-scroll {
      flex-direction: row;
      flex-wrap: wrap;
      gap: 0.5rem;
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
