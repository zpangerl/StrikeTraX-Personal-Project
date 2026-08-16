<template>
    <div class="text-center mt-3 pt-4">
        <h1 class="display-5"><strong>Game History</strong></h1>
    </div>
    <!--Will only appear if no game data is stored in database-->
    <div class="d-flex justify-content-center" v-if="!hasGameData && !isLoading">
        <h4 class="display-5">No games to display!</h4>
    </div>
    <!--Will only appear if any invalid games exist, giving the user the ability to purge invalid games-->
    <!--Invalid games in this context mean impossible scores, such as negative numbers, more than 10 pins in a frame, string instead of a number, etc-->
    <!--With the database, this shouldn't happen, but is technically still possible with devtools-->
    <div class="d-flex align-items-center flex-column" v-if="invalidGames.length !== 0">
        <h4 class="display-6">{{ invalidGames.length }} games could not be loaded due to invalid data</h4>
    </div>
    <!--Will only appear if the save data is corrupted-->
    <!--With the database this shouldn't happen, but is technically still possible with devtools-->
    <div class="d-flex align-items-center flex-column" v-if="hasCorruptedData">
        <h4 class="display-6">Saved game data corrupted, cannot load</h4>
    </div>
    <div class="d-flex align-items-center flex-column">
        <div v-for="(game, i) in gameHistory" :key="i" class="d-flex flex-column align-items-center">
            <!--Dynamically display each saved game including timestamp-->
            <h3 class="mt-4 mb-2">Game {{ i + 1 }}: {{ new Date(game.date).toLocaleString() }}</h3>
            <div class="scorecard d-flex">
                <div v-for="(frame, j) in game.frames" :key="j" class="frame-wrapper text-center me-2">
                    <div class="frame-number mb-1">{{ j + 1 }}</div>
                    <div class="frame-cell">
                        <div class="roll-boxes">
                            <div class="roll-box">{{ displayRoll(frame, 1) }}</div>
                            <div class="roll-box">{{ displayRoll(frame, 2) }}</div>
                            <!--Only frame 10 will have a roll3 field, need a check-->
                            <div class="roll-box" v-if="frame.roll3 !== undefined">{{ displayRoll(frame, 3) }}</div>
                        </div>
                        <div class="frame-total">{{ frame.currentTotal }}</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
  import { ref } from 'vue'
  import { displayRoll, calculateScore} from '../utils/scoring.js'
  const isLoading = ref(true)
  const hasGameData = ref(false)
  const invalidGames = ref([])
  const hasCorruptedData = ref(false)
  const gameHistory = ref([])
  loadGameHistory()

  /**
   * Loads and validates saved games from the database, converting each one into displayable frames.
   * Also populates invalidGames with indices of any games that fail validation.
   * Sets hasGameData to true if at least one valid game is found.
   * Sets isLoading to false so that the page will load after any games are retrieved.
   */
  async function loadGameHistory(){
    const response = await fetchSavedGames()
    if (!response) {
        isLoading.value = false
        return
    }
    const savedGames = response.games
    const savedFrames = []
    // iterate backwards to list games most-recent-first
    // update in the future after DB integration to introduce sort filters
    for (let i = savedGames.length - 1; i >= 0; i--){
        if (!savedGames[i] || !Array.isArray(savedGames[i].throws) || savedGames[i].throws.length === 0){
            invalidGames.value.push(i)
            continue
        }
        const calculateResult = calculateScore(savedGames[i].throws)
        if (!calculateResult.isValid){
            invalidGames.value.push(i)
            continue
        }
        const preparedGame = {
            date: savedGames[i].date,
            frames: calculateResult.frames
        }
        savedFrames.push(preparedGame)
    }
    if (savedFrames.length > 0) hasGameData.value = true
    gameHistory.value = savedFrames
    isLoading.value = false
  }

  /**
   * Fetches the user's list of completed games from the database, using the user's sessionID.
   * 
   * If no sessionID is in localStorage, there are no games to get, so simply return null.
   * 
   * This will be updated once login/auth is in place in phase 4.
   */
  async function fetchSavedGames(){
    let sessionID = localStorage.getItem('sessionID')
    if (sessionID === null){
        return null
    }
    // attempt to get the games from the database
    const response = await fetch(`http://127.0.0.1:8000/games?session_id=${sessionID}`)
    if (response.status === 422){
        alert("Invalid session ID")
        return null
    }
    else if (!response.ok){
        alert("Could not retrieve games, please try again")
        return null
    }
    else{
        let data = null
        try{
            data = await response.json()
        } catch (error){
            hasCorruptedData.value = true
            return null
        }
        return data
    }
  }

</script>