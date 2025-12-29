<script lang="ts">
  import { Icon } from '@immich/ui';
  import { mdiCamera, mdiMapMarker, mdiAccount, mdiClose, mdiImageMultiple } from '@mdi/js';
  import { DateTime } from 'luxon';
  import type { AssetResponseDto } from '@immich/sdk';
  import { AssetMediaSize } from '@immich/sdk';
  import { goto } from '$app/navigation';
  import { AppRoute } from '$lib/constants';

  interface Props {
    date: DateTime;
    assets: AssetResponseDto[];
    onClose: () => void;
  }

  let { date, assets, onClose }: Props = $props();

  // Format date
  const dayNumber = $derived(date.day);
  const dayName = $derived(date.toFormat('cccc')); // Full day name

  // Get unique locations
  const locations = $derived.by(() => {
    const locs = new Set<string>();
    for (const asset of assets) {
      const city = asset.exifInfo?.city;
      if (city) locs.add(city);
    }
    return Array.from(locs).slice(0, 2);
  });

  // Get unique people count
  const peopleCount = $derived.by(() => {
    const people = new Set<string>();
    for (const asset of assets) {
      for (const person of asset.people || []) {
        if (person.id) people.add(person.id);
      }
    }
    return people.size;
  });

  // Get unique tags
  const tags = $derived.by(() => {
    const tagMap = new Map<string, { name: string; color: string }>();
    for (const asset of assets) {
      for (const tag of asset.tags || []) {
        if (!tagMap.has(tag.id)) {
          tagMap.set(tag.id, {
            name: tag.value || tag.name || '',
            color: tag.color || '#4ade80',
          });
        }
      }
    }
    return Array.from(tagMap.values()).slice(0, 3);
  });

  // Get thumbnails for preview
  const thumbnails = $derived(
    assets.slice(0, 6).map((a) => ({
      id: a.id,
      url: `/api/assets/${a.id}/thumbnail?size=${AssetMediaSize.Thumbnail}`,
      count: assets.length,
    })),
  );

  function viewMemories() {
    if (assets.length > 0) {
      goto(`${AppRoute.PHOTOS}/${assets[0].id}`);
    }
  }
</script>

<div class="day-detail-panel">
  <!-- Close button -->
  <button type="button" class="close-btn" onclick={onClose}>
    <Icon icon={mdiClose} size="20" />
  </button>

  <!-- Header -->
  <div class="panel-header">
    <span class="day-number">{dayNumber}</span>
    <span class="separator">·</span>
    <span class="day-name">{dayName}</span>
  </div>

  <!-- Location and tags -->
  <div class="meta-row">
    {#if locations.length > 0}
      <div class="location">
        <Icon icon={mdiMapMarker} size="16" />
        <span>{locations.join(', ')}</span>
      </div>
    {/if}

    {#each tags as tag}
      <span class="tag-badge" style="background-color: {tag.color};">
        {tag.name}
      </span>
    {/each}
  </div>

  <!-- Stats -->
  <div class="stats-row">
    <div class="stat">
      <Icon icon={mdiCamera} size="16" />
      <span>{assets.length} fotos</span>
    </div>
    {#if peopleCount > 0}
      <span class="separator">·</span>
      <div class="stat">
        <Icon icon={mdiAccount} size="16" />
        <span>{peopleCount} personas</span>
      </div>
    {/if}
  </div>

  <!-- Thumbnails -->
  <div class="thumbnails-row">
    {#each thumbnails as thumb, i}
      <button type="button" class="thumb-card" onclick={() => goto(`${AppRoute.PHOTOS}/${thumb.id}`)}>
        <img src={thumb.url} alt="" loading="lazy" />
        {#if i === thumbnails.length - 1 && assets.length > thumbnails.length}
          <div class="thumb-badge">
            <Icon icon={mdiCamera} size="14" />
            <span>{assets.length}</span>
          </div>
        {/if}
      </button>
    {/each}
  </div>

  <!-- Action button -->
  <button type="button" class="view-btn" onclick={viewMemories}>
    <Icon icon={mdiImageMultiple} size="20" />
    <span>Ver recuerdos</span>
  </button>
</div>

<style>
  .day-detail-panel {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #1f1f1f;
    border-top-left-radius: 20px;
    border-top-right-radius: 20px;
    padding: 1.5rem;
    box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.5);
    z-index: 100;
    animation: slideUp 0.3s ease;
  }

  @keyframes slideUp {
    from {
      transform: translateY(100%);
    }
    to {
      transform: translateY(0);
    }
  }

  .close-btn {
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: none;
    border: none;
    color: #888;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 50%;
    transition: background 0.2s;
  }

  .close-btn:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  .panel-header {
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
  }

  .day-number {
    font-size: 2rem;
    font-weight: 300;
    color: white;
  }

  .separator {
    color: #666;
  }

  .day-name {
    font-size: 1.25rem;
    color: white;
  }

  .meta-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-bottom: 0.5rem;
  }

  .location {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    color: #4ade80;
    font-size: 0.875rem;
  }

  .tag-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    font-size: 0.75rem;
    color: white;
    font-weight: 500;
  }

  .stats-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #888;
    font-size: 0.875rem;
    margin-bottom: 1rem;
  }

  .stat {
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }

  .thumbnails-row {
    display: flex;
    gap: 0.5rem;
    overflow-x: auto;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
    scrollbar-width: thin;
  }

  .thumb-card {
    position: relative;
    flex-shrink: 0;
    width: 100px;
    height: 100px;
    border-radius: 12px;
    overflow: hidden;
    border: none;
    padding: 0;
    cursor: pointer;
    transition: transform 0.2s;
  }

  .thumb-card:hover {
    transform: scale(1.05);
  }

  .thumb-card img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .thumb-badge {
    position: absolute;
    bottom: 0.5rem;
    left: 0.5rem;
    background: rgba(0, 0, 0, 0.7);
    padding: 0.25rem 0.5rem;
    border-radius: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.25rem;
    color: white;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .view-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    width: 100%;
    padding: 0.875rem;
    background: #2a2a2a;
    border: 1px solid #333;
    border-radius: 2rem;
    color: white;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .view-btn:hover {
    background: #333;
    border-color: #444;
  }

  @media (min-width: 768px) {
    .day-detail-panel {
      left: auto;
      right: 1rem;
      bottom: 1rem;
      width: 400px;
      border-radius: 20px;
    }
  }
</style>
