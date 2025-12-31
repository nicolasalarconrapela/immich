<script lang="ts">
  import StarRating from '$lib/elements/StarRating.svelte';
  import { AssetMediaSize, type AssetResponseDto } from '@immich/sdk';
  import { Icon } from '@immich/ui';
  import {
    mdiCheckCircle,
    mdiCheckCircleOutline,
    mdiChevronLeft,
    mdiChevronRight,
    mdiClose,
    mdiHeart,
    mdiHeartOutline,
  } from '@mdi/js';
  import { onDestroy, onMount } from 'svelte';
  import { fade } from 'svelte/transition';

  interface Props {
    asset: AssetResponseDto;
    onClose: () => void;
    onToggleSelect?: (asset: AssetResponseDto) => void;
    onToggleFavorite?: (asset: AssetResponseDto) => void;
    onRatingChange?: (rating: number) => void;
    isSelected?: boolean;
    onNext?: () => void;
    onPrevious?: () => void;
  }

  let {
    asset,
    onClose,
    onToggleSelect,
    onToggleFavorite,
    onRatingChange,
    isSelected = false,
    onNext,
    onPrevious,
  }: Props = $props();

  let previewUrl = $derived(`/api/assets/${asset.id}/thumbnail?size=${AssetMediaSize.Preview}`);

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      onClose();
    } else if (e.key === 'ArrowRight' && onNext) {
      onNext();
    } else if (e.key === 'ArrowLeft' && onPrevious) {
      onPrevious();
    } else if (e.key === ' ' && onToggleSelect) {
      e.preventDefault(); // Prevent scroll
      onToggleSelect(asset);
    } else if (e.key.toLowerCase() === 'f' && onToggleFavorite) {
      onToggleFavorite(asset);
    }
  }

  // Lock body scroll
  onMount(() => {
    document.body.style.overflow = 'hidden';
  });

  onDestroy(() => {
    document.body.style.overflow = '';
  });
</script>

<svelte:window onkeydown={handleKeydown} />

<div class="lightbox-overlay" transition:fade={{ duration: 200 }}>
  <!-- Toolbar -->
  <div class="toolbar">
    <button type="button" class="icon-btn" onclick={onClose} aria-label="Close">
      <Icon icon={mdiClose} size="24" />
    </button>

    <div class="spacer"></div>

    <!-- Star Rating -->
    {#if onRatingChange}
      <div class="rating-container">
        <StarRating rating={asset.exifInfo?.rating || 0} onRating={onRatingChange} />
      </div>
    {/if}

    <!-- Favorite Toggle -->
    {#if onToggleFavorite}
      <button
        type="button"
        class="icon-btn favorite-btn"
        class:favorited={asset.isFavorite}
        onclick={() => onToggleFavorite && onToggleFavorite(asset)}
        title="Toggle Favorite (F)"
      >
        <Icon icon={asset.isFavorite ? mdiHeart : mdiHeartOutline} size="24" />
      </button>
    {/if}

    <!-- Selection Toggle -->
    {#if onToggleSelect}
      <button
        type="button"
        class="icon-btn select-btn"
        class:selected={isSelected}
        onclick={() => onToggleSelect && onToggleSelect(asset)}
        title="Toggle Selection (Space)"
      >
        <Icon icon={isSelected ? mdiCheckCircle : mdiCheckCircleOutline} size="24" />
        <span>{isSelected ? 'Selected' : 'Select'}</span>
      </button>
    {/if}
  </div>

  <!-- Main Image Area -->
  <div class="image-container">
    <img src={previewUrl} alt="Quick View" class="main-image" />
  </div>

  <!-- Navigation Arrows -->
  {#if onPrevious}
    <button type="button" class="nav-arrow left" onclick={onPrevious} aria-label="Previous">
      <Icon icon={mdiChevronLeft} size="48" />
    </button>
  {/if}

  {#if onNext}
    <button type="button" class="nav-arrow right" onclick={onNext} aria-label="Next">
      <Icon icon={mdiChevronRight} size="48" />
    </button>
  {/if}
</div>

<style>
  .lightbox-overlay {
    position: fixed;
    inset: 0;
    background-color: rgba(0, 0, 0, 0.95);
    z-index: 1000;
    display: flex;
    flex-direction: column;
    color: white;
    user-select: none;
  }

  .toolbar {
    display: flex;
    align-items: center;
    padding: 1rem;
    background: linear-gradient(to bottom, rgba(0, 0, 0, 0.8), transparent);
    z-index: 10;
  }

  .spacer {
    flex: 1;
  }

  .icon-btn {
    background: rgba(255, 255, 255, 0.1);
    border: none;
    color: white;
    padding: 0.5rem;
    border-radius: 50%;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .rating-container {
    padding: 0 1rem;
    color: white; /* Ensure stars are visible if they rely on currentColor */
    /* Force proper color on StarRating children if possible, primarily via class override in StarRating or here */
  }

  /* Override StarRating styles to work in dark overlay */
  :global(.rating-container .text-primary) {
    color: white !important;
  }

  .icon-btn:hover {
    background: rgba(255, 255, 255, 0.2);
  }

  .select-btn {
    border-radius: 2rem;
    padding-right: 1rem;
    background: rgba(0, 0, 0, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.3);
  }

  .select-btn.selected {
    background: #4ade80;
    color: black;
    border-color: #4ade80;
  }

  .favorite-btn.favorited {
    color: #ef4444; /* red-500 */
  }

  .image-container {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    padding: 1rem;
  }

  .main-image {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
  }

  .nav-arrow {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.5);
    cursor: pointer;
    padding: 2rem;
    transition: color 0.2s;
  }

  .nav-arrow:hover {
    color: white;
  }

  .left {
    left: 0;
  }
  .right {
    right: 0;
  }
</style>
