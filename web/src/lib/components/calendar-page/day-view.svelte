<script lang="ts">
  import { goto } from '$app/navigation';
  import { AppRoute } from '$lib/constants';
  import type { AssetResponseDto } from '@immich/sdk';
  import { AssetMediaSize, searchAssets } from '@immich/sdk';
  import { Icon } from '@immich/ui';
  import { mdiCamera, mdiChevronLeft, mdiChevronRight, mdiLoading } from '@mdi/js';
  import { DateTime } from 'luxon';

  interface Props {
    currentDate: DateTime;
    onNavigate: (direction: number) => void;
  }

  let { currentDate, onNavigate }: Props = $props();

  let assets: AssetResponseDto[] = $state([]);
  let isLoading = $state(true);

  // Hours of the day (0-23)
  const hours = Array.from({ length: 24 }, (_, i) => i);

  // Format date for header
  const formattedDate = $derived(currentDate.toFormat('cccc, d MMMM'));
  const isToday = $derived(currentDate.hasSame(DateTime.now(), 'day'));

  // Group assets by hour
  const assetsByHour = $derived.by(() => {
    const hourMap = new Map<number, AssetResponseDto[]>();

    // Initialize all hours
    for (let h = 0; h < 24; h++) {
      hourMap.set(h, []);
    }

    for (const asset of assets) {
      const assetDate = DateTime.fromISO(asset.fileCreatedAt);
      const hour = assetDate.hour;
      hourMap.get(hour)!.push(asset);
    }

    return hourMap;
  });

  // Total photos for the day
  const totalPhotos = $derived(assets.length);

  // Load assets for this day
  async function loadDayAssets() {
    isLoading = true;

    const startOfDay = currentDate.startOf('day');
    const endOfDay = currentDate.endOf('day');

    try {
      const result = await searchAssets({
        metadataSearchDto: {
          takenAfter: startOfDay.toISO() ?? undefined,
          takenBefore: endOfDay.toISO() ?? undefined,
          size: 500,
          withExif: true,
        },
      });

      assets = result.assets.items;
    } catch (error) {
      console.error('Failed to load day assets:', error);
    } finally {
      isLoading = false;
    }
  }

  function openAsset(assetId: string) {
    goto(`${AppRoute.PHOTOS}/${assetId}`);
  }

  function formatHour(hour: number): string {
    return DateTime.fromObject({ hour }).toFormat('HH:mm');
  }

  // Reload when date changes
  $effect(() => {
    currentDate; // dependency
    loadDayAssets();
  });
</script>

<div class="day-view">
  <!-- Day header -->
  <div class="day-header">
    <button type="button" class="nav-btn" onclick={() => onNavigate(-1)}>
      <Icon icon={mdiChevronLeft} size="24" />
    </button>

    <div class="date-info">
      <span class="date-text" class:today={isToday}>{formattedDate}</span>
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

  <!-- Timeline -->
  {#if isLoading}
    <div class="loading">
      <Icon icon={mdiLoading} size="48" class="animate-spin" />
    </div>
  {:else}
    <div class="timeline">
      {#each hours as hour}
        {@const hourAssets = assetsByHour.get(hour) || []}
        {@const hasAssets = hourAssets.length > 0}

        <div class="hour-row" class:has-assets={hasAssets}>
          <!-- Hour label -->
          <div class="hour-label">
            <span class="hour-time">{formatHour(hour)}</span>
          </div>

          <!-- Timeline line and dot -->
          <div class="timeline-marker">
            <div class="timeline-line"></div>
            {#if hasAssets}
              <div class="timeline-dot"></div>
            {/if}
          </div>

          <!-- Content area -->
          <div class="hour-content">
            {#if hasAssets}
              <div class="assets-grid">
                {#each hourAssets.slice(0, 8) as asset, i}
                  <button type="button" class="asset-thumb" onclick={() => openAsset(asset.id)}>
                    <img
                      src={`/api/assets/${asset.id}/thumbnail?size=${AssetMediaSize.Thumbnail}`}
                      alt=""
                      loading="lazy"
                    />
                    {#if i === 7 && hourAssets.length > 8}
                      <div class="more-overlay">
                        +{hourAssets.length - 8}
                      </div>
                    {/if}
                  </button>
                {/each}
              </div>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .day-view {
    height: 100%;
    display: flex;
    flex-direction: column;
    background: #0a0a0a;
  }

  .day-header {
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

  .date-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
  }

  .date-text {
    font-size: 1.125rem;
    font-weight: 500;
    color: white;
    text-transform: capitalize;
  }

  .date-text.today {
    color: #4ade80;
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

  .timeline {
    flex: 1;
    overflow-y: auto;
    padding: 0 1rem;
  }

  .hour-row {
    display: flex;
    align-items: flex-start;
    min-height: 48px;
    opacity: 0.4;
    transition: opacity 0.2s;
  }

  .hour-row.has-assets {
    opacity: 1;
    min-height: auto;
    padding: 0.5rem 0;
  }

  .hour-label {
    width: 50px;
    flex-shrink: 0;
    padding-top: 2px;
  }

  .hour-time {
    font-size: 0.75rem;
    color: #666;
    font-weight: 500;
  }

  .has-assets .hour-time {
    color: #f97316;
  }

  .timeline-marker {
    width: 24px;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
  }

  .timeline-line {
    position: absolute;
    top: 0;
    bottom: 0;
    width: 2px;
    background: #333;
  }

  .timeline-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #f97316;
    border: 2px solid #0a0a0a;
    z-index: 1;
    margin-top: 4px;
  }

  .hour-content {
    flex: 1;
    min-width: 0;
    padding-left: 0.75rem;
  }

  .assets-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .asset-thumb {
    position: relative;
    width: 64px;
    height: 64px;
    border-radius: 8px;
    overflow: hidden;
    border: none;
    padding: 0;
    cursor: pointer;
    transition:
      transform 0.2s,
      box-shadow 0.2s;
  }

  .asset-thumb:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  }

  .asset-thumb img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .more-overlay {
    position: absolute;
    inset: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 0.875rem;
    font-weight: 600;
  }

  @media (min-width: 768px) {
    .asset-thumb {
      width: 80px;
      height: 80px;
    }
  }
</style>
