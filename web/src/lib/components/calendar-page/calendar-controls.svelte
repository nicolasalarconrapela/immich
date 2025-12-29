<script lang="ts">
  import { Icon } from '@immich/ui';
  import { mdiCalendarToday, mdiChevronLeft, mdiChevronRight } from '@mdi/js';
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

  const monthYear = $derived(currentDate.toFormat('MMMM yyyy'));
</script>

<div class="flex items-center gap-2">
  <!-- Navigation buttons -->
  <div class="flex items-center gap-1">
    <button
      type="button"
      class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
      onclick={onPrevious}
      title={$t('previous')}
    >
      <Icon icon={mdiChevronLeft} size="24" />
    </button>

    <button
      type="button"
      class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
      onclick={onNext}
      title={$t('next')}
    >
      <Icon icon={mdiChevronRight} size="24" />
    </button>
  </div>

  <!-- Current month/year display -->
  <span class="text-lg font-semibold min-w-[160px] text-center">
    {monthYear}
  </span>

  <!-- Today button -->
  <button
    type="button"
    class="flex items-center gap-1 px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600
           hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-sm"
    onclick={onToday}
  >
    <Icon icon={mdiCalendarToday} size="18" />
    <span class="hidden sm:inline">{$t('today')}</span>
  </button>

  <!-- View mode selector (future enhancement) -->
  <!-- <div class="hidden md:flex items-center gap-1 ml-4">
    <button
      type="button"
      class="px-3 py-1.5 text-sm rounded-lg transition-colors
        {viewMode === 'month' ? 'bg-immich-primary text-white' : 'hover:bg-gray-100 dark:hover:bg-gray-800'}"
      onclick={() => viewMode = 'month'}
    >
      {$t('month')}
    </button>
    <button
      type="button"
      class="px-3 py-1.5 text-sm rounded-lg transition-colors
        {viewMode === 'week' ? 'bg-immich-primary text-white' : 'hover:bg-gray-100 dark:hover:bg-gray-800'}"
      onclick={() => viewMode = 'week'}
    >
      {$t('week')}
    </button>
  </div> -->
</div>
