<script lang="ts">
  import { AssetMediaSize, type AssetResponseDto } from '@immich/sdk';
  import { Icon } from '@immich/ui';
  import { mdiCheckCircle, mdiCheckCircleOutline, mdiClose } from '@mdi/js';
  import { onDestroy, onMount } from 'svelte';
  import { fade } from 'svelte/transition';
  interface Props {
    asset: AssetResponseDto;
    onClose: () => void;
    onToggleSelect?: (asset: AssetResponseDto) => void;
    isSelected?: boolean;
    onNext?: () => void;
    onPrevious?: () => void;
  }

  let { asset, onClose, onToggleSelect, isSelected = false, onNext, onPrevious }: Props = $props();

  let previewUrl = $derived(`/api/assets/${asset.id}/thumbnail?size=${AssetMediaSize.Preview}`);
  let originalUrl = $derived(`/api/assets/${asset.id}/original`);

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
    <button class="icon-btn" onclick={onClose} aria-label="Close">
      <Icon icon={mdiClose} size="24" />
    </button>

    <div class="spacer"></div>

    <!-- Selection Toggle -->
    {#if onToggleSelect}
      <button
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
    <button class="nav-arrow left" onclick={onPrevious} aria-label="Previous">
      <Icon icon={mdiChevronLeft} size="48" />
    </button>
  {/if}

  {#if onNext}
    <button class="nav-arrow right" onclick={onNext} aria-label="Next">
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
