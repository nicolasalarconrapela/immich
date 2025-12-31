<script lang="ts">
  import { Icon } from '@immich/ui';
  import { mdiCalendar, mdiChevronLeft, mdiChevronRight } from '@mdi/js';
  import { DateTime } from 'luxon';
  import { t } from 'svelte-i18n';

  type ViewMode = 'day' | 'week' | '2weeks' | 'month' | 'year' | 'agenda';

  interface ViewOption {
    value: ViewMode;
    label: string;
    shortcut: string;
  }

  interface Props {
    currentDate: DateTime;
    onPrevious: () => void;
    onNext: () => void;
    onToday: () => void;
    onJumpToDate: (date: DateTime) => void;
    viewMode: ViewMode;
  }

  let { currentDate, onPrevious, onNext, onToday, onJumpToDate, viewMode = $bindable() }: Props = $props();

  let showDropdown = $state(false);
  let dateInput: HTMLInputElement;

  const viewOptions: ViewOption[] = [
    { value: 'day', label: 'Día', shortcut: 'D' },
    { value: 'week', label: 'Semana', shortcut: 'W' },
    { value: 'month', label: 'Mes', shortcut: 'M' },
    { value: 'year', label: 'Año', shortcut: 'Y' },
    { value: 'agenda', label: 'Agenda', shortcut: 'A' },
    { value: '2weeks', label: '2 semanas', shortcut: 'X' },
  ];

  const currentViewLabel = $derived(viewOptions.find((v) => v.value === viewMode)?.label || 'Mes');

  const monthYear = $derived(currentDate.toFormat('MMMM'));
  const year = $derived(currentDate.year);

  function selectView(view: ViewMode) {
    viewMode = view;
    showDropdown = false;
  }

  function toggleDropdown() {
    showDropdown = !showDropdown;
  }

  function closeDropdown() {
    showDropdown = false;
  }

  function handleJumpClick() {
    if (dateInput.showPicker) {
      dateInput.showPicker();
    } else {
      dateInput.click();
    }
  }

  function onDatePicked(event: Event) {
    const val = (event.target as HTMLInputElement).value;
    if (val) {
      onJumpToDate(DateTime.fromISO(val));
    }
  }
</script>

<svelte:window on:click={closeDropdown} />

<div class="controls-container">
  <!-- Navigation -->
  <div class="nav-buttons">
    <button type="button" class="nav-btn" onclick={onPrevious} title={$t('previous')}>
      <Icon icon={mdiChevronLeft} size="24" />
    </button>

    <button type="button" class="nav-btn" onclick={onNext} title={$t('next')}>
      <Icon icon={mdiChevronRight} size="24" />
    </button>
  </div>

  <!-- Date Controls (Pill: Today | Jump to date) -->
  <div class="date-controls">
    <button class="date-btn" onclick={onToday}>Today</button>
    <div class="separator"></div>
    <button class="date-btn icon-text" onclick={handleJumpClick}>
      <Icon icon={mdiCalendar} size="16" />
      <span>{monthYear} {year}</span>
    </button>

    <!-- Hidden Native Date Input -->
    <input
      type="date"
      bind:this={dateInput}
      class="hidden-input"
      onchange={onDatePicked}
      onclick={(e) => e.stopPropagation()}
    />
  </div>

  <!-- View Switcher (Tab Style) -->
  <div class="view-switcher">
    <button class="segment-btn" class:active={viewMode === 'year'} onclick={() => selectView('year')}> Año </button>
    <button class="segment-btn" class:active={viewMode === 'month'} onclick={() => selectView('month')}> Mes </button>
    <button class="segment-btn" class:active={viewMode === 'week'} onclick={() => selectView('week')}> Semana </button>
    <button class="segment-btn" class:active={viewMode === 'day'} onclick={() => selectView('day')}> Día </button>
  </div>
</div>

<style>
  .controls-container {
    display: flex;
    align-items: center;
    gap: 1rem;
    width: 100%;
    justify-content: space-between;
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

  /* Date Controls Pill */
  .date-controls {
    display: flex;
    align-items: center;
    background: #2a2a2a; /* Match UI theme */
    border: 1px solid #444;
    border-radius: 0.75rem;
    padding: 0.25rem;
    position: relative;
    min-height: 38px;
  }

  .date-btn {
    background: transparent;
    border: none;
    color: #e5e5e5;
    font-size: 0.875rem;
    font-weight: 600;
    padding: 0.25rem 0.75rem;
    cursor: pointer;
    transition: color 0.2s;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .date-btn:hover {
    color: white;
  }

  .icon-text {
    text-transform: capitalize;
  }

  .separator {
    width: 1px;
    height: 16px;
    background: rgba(255, 255, 255, 0.2);
  }

  .hidden-input {
    position: absolute;
    top: 0;
    left: 0;
    width: 0;
    height: 0;
    opacity: 0;
    pointer-events: none;
  }

  /* Segmented Control (Tabs) */
  .view-switcher {
    display: flex;
    background: #2a2a2a;
    border: 1px solid #444;
    border-radius: 0.75rem;
    padding: 4px;
    gap: 4px;
    margin-left: auto;
  }

  .segment-btn {
    background: transparent;
    border: none;
    color: #9ca3af;
    padding: 0.35rem 1rem;
    border-radius: 0.5rem;
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .segment-btn:hover {
    color: white;
  }

  .segment-btn.active {
    background: #4ade80; /* Accent Color */
    color: #000;
    font-weight: 700;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  }

  @media (max-width: 640px) {
    .date-controls {
      display: none;
    }
  }
</style>
