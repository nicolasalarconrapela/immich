<script lang="ts">
  import { Icon } from '@immich/ui';
  import { mdiChevronDown, mdiChevronLeft, mdiChevronRight } from '@mdi/js';
  import { DateTime } from 'luxon';
  import { t } from 'svelte-i18n';

  interface Props {
    currentDate: DateTime;
    onPrevious: () => void;
    onNext: () => void;
    onToday: () => void;
    viewMode: 'month' | 'week' | 'day';
  }

  let { currentDate, onPrevious, onNext, onToday, viewMode = $bindable() }: Props = $props();

  const monthYear = $derived(currentDate.toFormat('MMMM'));
  const year = $derived(currentDate.year);
</script>

<div class="controls-container">
  <!-- Month selector -->
  <button type="button" class="month-selector">
    <span class="month-name">{monthYear}</span>
    <Icon icon={mdiChevronDown} size="20" />
  </button>

  <!-- Navigation -->
  <div class="nav-buttons">
    <button type="button" class="nav-btn" onclick={onPrevious} title={$t('previous')}>
      <Icon icon={mdiChevronLeft} size="24" />
    </button>

    <button type="button" class="nav-btn" onclick={onNext} title={$t('next')}>
      <Icon icon={mdiChevronRight} size="24" />
    </button>
  </div>

  <!-- Today button -->
  <button type="button" class="today-btn" onclick={onToday} title={$t('today')}>
    <span class="today-number">{DateTime.now().day}</span>
  </button>
</div>

<style>
  .controls-container {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .month-selector {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    background: none;
    border: none;
    color: white;
    font-size: 1.25rem;
    font-weight: 400;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 0.5rem;
    transition: background 0.2s;
  }

  .month-selector:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  .month-name {
    text-transform: capitalize;
  }

  .nav-buttons {
    display: flex;
    align-items: center;
    gap: 0.25rem;
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

  .today-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    background: none;
    border: 2px solid currentColor;
    border-radius: 0.5rem;
    color: white;
    cursor: pointer;
    transition: all 0.2s;
  }

  .today-btn:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  .today-number {
    font-size: 0.875rem;
    font-weight: 600;
  }
</style>
