import { Component, createSignal, createEffect, Show } from 'solid-js';

import styles from './App.module.css';
import { Menu } from './components/menu/Menu';
import logo from './assets/logo.webp'
import leaf from './assets/leaf.png'
import gdelt from './assets/gdelt.png'
import trends from './assets/trends.png'
import bigquery from './assets/bigquery.png'

const App: Component = () => {
  //  const [plantsUrl, setPlantsUrl] = createSignal("https://wikipediascraper-qtw3rvj3ya-ew.a.run.app/tables?site=https://en.wikipedia.org/wiki/List_of_plants_used_in_herbalism&flatten=true")
  const [plantsUrl, setPlantsUrl] = createSignal("https://wikipediascraper-qtw3rvj3ya-ew.a.run.app/tables?site=https://en.wikipedia.org/wiki/List_of_plants_used_in_herbalism&flatten=true")
  const [selectedPlant, setSelectedPlant] = createSignal("")
  const [detailUrl, setDetailUrl] = createSignal("https://www.wikipedia.org")
  const [filter, setFilter] = createSignal("")

  createEffect(() => {
    console.info(selectedPlant())
    setDetailUrl(`https://api.gdeltproject.org/api/v2/summary/summary?d=web&t=summary&k=${selectedPlant().replace("-", "+").replace(" or ", " ").split(",")[0]}+plant&ts=full&svt=zoom&sgt=yes&stc=yes&sta=list&c=1`)
  });

  return (
    <div>
      <div class={styles.navbar}>
        <img class={styles.header_logo} src={logo}></img>
        <span class={styles.header_text} onclick={(e) => setSelectedPlant("")}>Herbal Plant Trends Dashboard</span>
        <div style={{ "margin-left": "auto" }}>
          <a href="https://cloud.google.com/bigquery" target="_blank"><img class={styles.header_gdelt} src={bigquery}></img></a>
          <a href="https://trends.google.com/" target="_blank"><img class={styles.header_gdelt} src={trends}></img></a>
          <a href="https://www.gdeltproject.org/" target="_blank"><img class={styles.header_gdelt} src={gdelt}></img></a>
        </div>
      </div>
      <div class={styles.app_container}>
        <div class={styles.menu_frame} >
          <div class={styles.search_box}>
            <span class={styles.search_icon + " material-symbols-outlined"}>filter_list</span>
            <input class={styles.search_field} oninput={(e) => setFilter(e.target.value)} placeholder="Filter"></input>
          </div>
          <Menu data={plantsUrl()} setSelected={setSelectedPlant} filter={filter()}></Menu>
        </div>
        <Show when={selectedPlant() != ""}>
          <div class={styles.detail_header}>
            {selectedPlant()}
          </div>
          <iframe class={styles.detail_frame} src={detailUrl()}></iframe>
        </Show>
        {/* <Show when={selectedPlant() == ""}>
          <div style={{ "flex-grow": 1 }}>
            <h1>Trending plants</h1>
            <div style={{ display: "flex", "flex-grow": 1, "justify-content": "space-evenly" }}>
              <div style={{ width: "100px", "background-color": "red" }}>test</div>
              <div style={{ width: "100px", "background-color": "red" }}>test</div>

              <div style={{ width: "100px", "background-color": "red" }}>test</div>

            </div>
          </div>
        </Show> */}
        <Show when={selectedPlant() == ""}>
          <div class={styles.detail_empty_frame} >
            <div class={styles.detail_empty_message}>
              <img class={styles.detail_image} src={leaf}></img><br></br>
              Please select a plant from the list on the left.
            </div>
          </div>
        </Show>
      </div >
    </div>
  );
};

export default App;
