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
          {totalPhotos} memories
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
  :global(:root) {
    --cal-bg: #0f172a; /* Slate 900 */
    --cal-cell-bg: #1e293b; /* Slate 800 */
    --cal-accent: #38bdf8; /* Sky 400 */
    --cal-text: #f8fafc; /* Slate 50 */
    --cal-text-muted: #94a3b8; /* Slate 400 */
  }

  .day-view {
    height: 100%;
    display: flex;
    flex-direction: column;
    background: var(--cal-bg);
    color: var(--cal-text);
  }

  .day-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.5rem 2rem;
    position: sticky;
    top: 0;
    background: rgba(15, 23, 42, 0.9);
    backdrop-filter: blur(10px);
    z-index: 20;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  }

  .nav-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.05);
    color: var(--cal-text);
    padding: 0.5rem;
    border-radius: 50%;
    cursor: pointer;
    transition: all 0.2s;
  }

  .nav-btn:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: scale(1.1);
  }

  .date-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
  }

  .date-text {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--cal-text);
    text-transform: capitalize;
  }

  .date-text.today {
    color: var(--cal-accent);
  }

  .photo-count {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.8rem;
    color: var(--cal-text-muted);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .loading {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--cal-accent);
  }

  .timeline {
    flex: 1;
    overflow-y: auto;
    padding: 1rem 2rem;
  }

  .hour-row {
    display: flex;
    align-items: flex-start;
    min-height: 60px;
    opacity: 0.3;
    transition: opacity 0.3s;
  }

  .hour-row.has-assets {
    opacity: 1;
    min-height: auto;
    padding: 1rem 0;
  }

  .hour-label {
    width: 60px;
    flex-shrink: 0;
    padding-top: 6px;
    text-align: right;
    padding-right: 1rem;
  }

  .hour-time {
    font-size: 0.8rem;
    color: var(--cal-text-muted);
    font-weight: 600;
    letter-spacing: 0.05em;
  }

  .has-assets .hour-time {
    color: var(--cal-accent);
  }

  .timeline-marker {
    width: 24px;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    margin-right: 1rem;
  }

  .timeline-line {
    position: absolute;
    top: 0;
    bottom: 0;
    width: 2px;
    background: rgba(255, 255, 255, 0.1);
  }

  .timeline-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--cal-accent);
    border: 3px solid var(--cal-bg);
    z-index: 10;
    margin-top: 8px;
    box-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
  }

  .hour-content {
    flex: 1;
    min-width: 0;
    padding-bottom: 1rem;
  }

  .assets-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 0.75rem;
  }

  .asset-thumb {
    position: relative;
    aspect-ratio: 1;
    border-radius: 0.75rem;
    overflow: hidden;
    border: none;
    padding: 0;
    cursor: pointer;
    transition:
      transform 0.2s cubic-bezier(0.4, 0, 0.2, 1),
      box-shadow 0.2s;
  }

  .asset-thumb:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
    z-index: 5;
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
    font-size: 1rem;
    font-weight: 700;
    backdrop-filter: blur(2px);
  }

  @media (max-width: 768px) {
    .day-header {
      padding: 1rem;
    }

    .timeline {
      padding: 1rem;
    }

    .hour-label {
      width: 45px;
      font-size: 0.75rem;
      padding-right: 0.5rem;
    }

    .timeline-marker {
      margin-right: 0.5rem;
    }
  }
</style>
