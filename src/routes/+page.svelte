<script lang="ts">
    import {MapLibre, VectorTileSource, LineLayer} from 'svelte-maplibre';
</script>

<MapLibre
    style="https://www.karadzhov.com/meridian/basic-style.json"
    standardControls
    center={[25.4858, 42.7339]}
    zoom={6}
>
</MapLibre>
