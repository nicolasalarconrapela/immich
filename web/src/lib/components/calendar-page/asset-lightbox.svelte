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
    mdiMagnifyMinus,
    mdiMagnifyPlus,
    mdiMagnifyRemoveOutline,
  } from '@mdi/js';
  import { onDestroy, onMount } from 'svelte';
  import { fade } from 'svelte/transition';

  interface Props {
    asset: AssetResponseDto;
    assets?: AssetResponseDto[];
    onClose: () => void;
    onToggleSelect?: (asset: AssetResponseDto) => void;
    onToggleFavorite?: (asset: AssetResponseDto) => void;
    onRatingChange?: (rating: number) => void;
    onNavigateTo?: (asset: AssetResponseDto) => void;
    isSelected?: boolean;
    onNext?: () => void;
    onPrevious?: () => void;
  }

  let {
    asset,
    assets = [],
    onClose,
    onToggleSelect,
    onToggleFavorite,
    onRatingChange,
    onNavigateTo,
    isSelected = false,
    onNext,
    onPrevious,
  }: Props = $props();

  let previewUrl = $derived(`/api/assets/${asset.id}/thumbnail?size=${AssetMediaSize.Preview}`);

  // Zoom state
  let zoomLevel = $state(1);
  let panX = $state(0);
  let panY = $state(0);
  let isDragging = $state(false);
  let dragStartX = 0;
  let dragStartY = 0;
  let imageRef: HTMLImageElement | null = null;

  const MIN_ZOOM = 1;
  const MAX_ZOOM = 5;
  const ZOOM_STEP = 0.5;

  // Filmstrip visibility
  let showFilmstrip = $state(true);

  function zoomIn() {
    zoomLevel = Math.min(zoomLevel + ZOOM_STEP, MAX_ZOOM);
  }

  function zoomOut() {
    zoomLevel = Math.max(zoomLevel - ZOOM_STEP, MIN_ZOOM);
    if (zoomLevel === 1) {
      panX = 0;
      panY = 0;
    }
  }

  function resetZoom() {
    zoomLevel = 1;
    panX = 0;
    panY = 0;
  }

  function handleWheel(e: WheelEvent) {
    e.preventDefault();
    if (e.deltaY < 0) {
      zoomIn();
    } else {
      zoomOut();
    }
  }

  function handleMouseDown(e: MouseEvent) {
    if (zoomLevel > 1) {
      isDragging = true;
      dragStartX = e.clientX - panX;
      dragStartY = e.clientY - panY;
    }
  }

  function handleMouseMove(e: MouseEvent) {
    if (isDragging && zoomLevel > 1) {
      panX = e.clientX - dragStartX;
      panY = e.clientY - dragStartY;
    }
  }

  function handleMouseUp() {
    isDragging = false;
  }

  // Reset zoom when asset changes
  $effect(() => {
    asset; // dependency
    resetZoom();
  });

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      onClose();
    } else if (e.key === 'ArrowRight' && onNext) {
      onNext();
    } else if (e.key === 'ArrowLeft' && onPrevious) {
      onPrevious();
    } else if (e.key === ' ' && onToggleSelect) {
      e.preventDefault();
      onToggleSelect(asset);
    } else if (e.key.toLowerCase() === 'f' && onToggleFavorite) {
      onToggleFavorite(asset);
    } else if (e.key === '+' || e.key === '=') {
      zoomIn();
    } else if (e.key === '-') {
      zoomOut();
    } else if (e.key === '0') {
      resetZoom();
    }
  }

  function navigateToAsset(targetAsset: AssetResponseDto) {
    if (onNavigateTo) {
      onNavigateTo(targetAsset);
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

<svelte:window onkeydown={handleKeydown} onmouseup={handleMouseUp} onmousemove={handleMouseMove} />

<div class="lightbox-overlay" transition:fade={{ duration: 200 }}>
  <!-- Toolbar -->
  <div class="toolbar">
    <button type="button" class="icon-btn" onclick={onClose} aria-label="Close">
      <Icon icon={mdiClose} size="24" />
    </button>

    <!-- Zoom Controls -->
    <div class="zoom-controls">
      <button type="button" class="icon-btn" onclick={zoomOut} aria-label="Zoom Out" disabled={zoomLevel <= MIN_ZOOM}>
        <Icon icon={mdiMagnifyMinus} size="20" />
      </button>
      <span class="zoom-level">{Math.round(zoomLevel * 100)}%</span>
      <button type="button" class="icon-btn" onclick={zoomIn} aria-label="Zoom In" disabled={zoomLevel >= MAX_ZOOM}>
        <Icon icon={mdiMagnifyPlus} size="20" />
      </button>
      {#if zoomLevel > 1}
        <button type="button" class="icon-btn" onclick={resetZoom} aria-label="Reset Zoom">
          <Icon icon={mdiMagnifyRemoveOutline} size="20" />
        </button>
      {/if}
    </div>

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
  <div class="image-container" class:dragging={isDragging} onwheel={handleWheel} onmousedown={handleMouseDown}>
    <img
      bind:this={imageRef}
      src={previewUrl}
      alt="Quick View"
      class="main-image"
      style="transform: scale({zoomLevel}) translate({panX / zoomLevel}px, {panY / zoomLevel}px);"
      draggable="false"
    />
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

  <!-- Filmstrip -->
  {#if assets.length > 1 && showFilmstrip}
    <div class="filmstrip">
      <div class="filmstrip-scroll">
        {#each assets as thumbAsset, index}
          <button
            type="button"
            class="filmstrip-thumb"
            class:active={thumbAsset.id === asset.id}
            onclick={() => navigateToAsset(thumbAsset)}
            aria-label="Go to image {index + 1}"
          >
            <img
              src={`/api/assets/${thumbAsset.id}/thumbnail?size=${AssetMediaSize.Thumbnail}`}
              alt=""
              loading="lazy"
            />
          </button>
        {/each}
      </div>
    </div>
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
    gap: 0.5rem;
  }

  .zoom-controls {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    margin-left: 1rem;
    background: rgba(0, 0, 0, 0.5);
    padding: 0.25rem 0.5rem;
    border-radius: 2rem;
  }

  .zoom-level {
    font-size: 0.75rem;
    min-width: 3rem;
    text-align: center;
    color: rgba(255, 255, 255, 0.8);
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

  .icon-btn:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }

  .rating-container {
    padding: 0 1rem;
    color: white;
  }

  :global(.rating-container .text-primary) {
    color: white !important;
  }

  .icon-btn:hover:not(:disabled) {
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
    color: #ef4444;
  }

  .image-container {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    padding: 1rem;
    cursor: grab;
  }

  .image-container.dragging {
    cursor: grabbing;
  }

  .main-image {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
    transition: transform 0.1s ease-out;
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
    z-index: 15;
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

  /* Filmstrip */
  .filmstrip {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(to top, rgba(0, 0, 0, 0.9), transparent);
    padding: 1rem;
    z-index: 10;
  }

  .filmstrip-scroll {
    display: flex;
    gap: 0.5rem;
    overflow-x: auto;
    justify-content: center;
    padding: 0.5rem 0;
    scrollbar-width: thin;
    scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
  }

  .filmstrip-thumb {
    flex-shrink: 0;
    width: 60px;
    height: 60px;
    border-radius: 0.25rem;
    overflow: hidden;
    border: 2px solid transparent;
    padding: 0;
    background: #000;
    cursor: pointer;
    transition: all 0.2s;
    opacity: 0.6;
  }

  .filmstrip-thumb:hover {
    opacity: 1;
    border-color: rgba(255, 255, 255, 0.5);
  }

  .filmstrip-thumb.active {
    opacity: 1;
    border-color: #38bdf8;
    box-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
  }

  .filmstrip-thumb img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
</style>
