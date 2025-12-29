<script lang="ts">
  import { goto } from '$app/navigation';
  import ImageThumbnail from '$lib/components/assets/thumbnail/image-thumbnail.svelte';
  import { AppRoute } from '$lib/constants';
  import type { AssetResponseDto } from '@immich/sdk';
  import { AssetMediaSize, searchAssets } from '@immich/sdk';
  import { Icon } from '@immich/ui';
  import { mdiArrowLeft, mdiLoading } from '@mdi/js';
  import { DateTime } from 'luxon';
  import { t } from 'svelte-i18n';

  interface Props {
    date: DateTime;
    onBack: () => void;
  }

  let { date, onBack }: Props = $props();

  let assets: AssetResponseDto[] = $state([]);
  let isLoading = $state(true);

  const formattedDate = $derived(date.toLocaleString(DateTime.DATE_FULL));

  // Group assets by hour
  const assetsByHour = $derived.by(() => {
    const hourMap = new Map<number, AssetResponseDto[]>();

    for (const asset of assets) {
      const assetDate = DateTime.fromISO(asset.fileCreatedAt);
      const hour = assetDate.hour;

      if (!hourMap.has(hour)) {
        hourMap.set(hour, []);
      }
      hourMap.get(hour)!.push(asset);
    }

    // Sort by hour
    return Array.from(hourMap.entries()).sort((a, b) => a[0] - b[0]);
  });

  // Load assets for this day
  async function loadDayAssets() {
    isLoading = true;

    const startOfDay = date.startOf('day');
    const endOfDay = date.endOf('day');

    try {
      const result = await searchAssets({
        metadataSearchDto: {
          takenAfter: startOfDay.toISO() ?? undefined,
          takenBefore: endOfDay.toISO() ?? undefined,
          size: 200,
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

  $effect(() => {
    loadDayAssets();
  });
</script>

<div class="flex flex-col h-full">
  <!-- Header -->
  <div class="flex items-center gap-4 p-4 border-b dark:border-gray-700">
    <button
      type="button"
      class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
      onclick={onBack}
      title={$t('back')}
    >
      <Icon icon={mdiArrowLeft} size="24" />
    </button>

    <div>
      <h2 class="text-xl font-semibold">{formattedDate}</h2>
      <p class="text-sm text-gray-500 dark:text-gray-400">
        {assets.length}
        {$t('photos')}
      </p>
    </div>
  </div>

  <!-- Content -->
  {#if isLoading}
    <div class="flex items-center justify-center flex-1">
      <Icon icon={mdiLoading} size="48" class="animate-spin text-immich-primary" />
    </div>
  {:else if assets.length === 0}
    <div class="flex items-center justify-center flex-1 text-gray-500">
      {$t('no_results')}
    </div>
  {:else}
    <div class="flex-1 overflow-y-auto p-4">
      <!-- Timeline view -->
      <div class="relative">
        <!-- Timeline line -->
        <div class="absolute left-[60px] top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700"></div>

        {#each assetsByHour as [hour, hourAssets]}
          <div class="relative flex gap-4 mb-6">
            <!-- Hour label -->
            <div class="w-[60px] shrink-0 text-right pr-4">
              <span class="text-sm font-medium text-gray-500 dark:text-gray-400">
                {formatHour(hour)}
              </span>
            </div>

            <!-- Timeline dot -->
            <div
              class="absolute left-[56px] top-1 w-3 h-3 rounded-full bg-immich-primary dark:bg-immich-dark-primary z-10"
            ></div>

            <!-- Assets grid -->
            <div class="flex-1 ml-4">
              <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-2">
                {#each hourAssets as asset}
                  <button
                    type="button"
                    class="aspect-square rounded-lg overflow-hidden hover:ring-2 hover:ring-immich-primary
                           transition-all hover:scale-105"
                    onclick={() => openAsset(asset.id)}
                  >
                    <ImageThumbnail
                      url={`/api/assets/${asset.id}/thumbnail?size=${AssetMediaSize.Thumbnail}`}
                      altText={asset.originalFileName}
                      widthStyle="100%"
                    />
                  </button>
                {/each}
              </div>
            </div>
          </div>
        {/each}
      </div>
    </div>
  {/if}
</div>

<style>
  /* Custom scrollbar for the day view */
  .overflow-y-auto {
    scrollbar-width: thin;
  }
</style>
