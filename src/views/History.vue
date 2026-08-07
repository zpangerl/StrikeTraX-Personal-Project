<template>
    <div class="text-center mt-3 pt-4">
        <h1 class="display-5"><strong>Game History</strong></h1>
    </div>
    <!--Will only appear if no game data is stored in localStorage, will be changed to check DB in the future-->
    <div class="d-flex justify-content-center" v-if="!hasGameData">
        <h4 class="display-5">No games to display!</h4>
    </div>
    <!--Will only appear if any invalid games exist, giving the user the ability to purge invalid games-->
    <!--Invalid games in this context mean impossible scores, such as negative numbers, more than 10 pins in a frame, string instead of a number, etc-->
    <div class="d-flex align-items-center flex-column" v-if="invalidGames.length !== 0">
        <h4 class="display-6">{{ invalidGames.length }} games could not be loaded due to invalid data</h4>
        <button class="btn btn-primary" @click="removeInvalidGames">Remove Invalid Games</button>
    </div>
    <!--Will only appear if the save data is corrupted-->
    <!--Corrupted save data requires invalid JSON syntax-->
    <div class="d-flex align-items-center flex-column" v-if="hasCorruptedData">
        <h4 class="display-6">Saved game data corrupted, cannot load</h4>
        <h4>Please click below to reset all saved data</h4>
        <button class="btn btn-danger" @click="resetGames">Reset Saved Data</button>
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

<script>
    import { ref, computed } from 'vue'
    import { displayRoll, calculateScore} from '../utils/scoring.js'
    export default {
        setup(){
            const invalidGames = ref([])
            const hasCorruptedData = ref(false)
            const hasGameData = ref(false)

            /**
             * Loads and validates saved games from localStorage, converting each one into displayable frames.
             * Also populates invalidGames with indices of any games that fail validation for easy clean up.
             * Sets hasGameData to true if at least one valid game is found.
             * 
             * @returns {Object[]} - An array of valid games, newest first, each with a date and computed frames.
             */
            const gameHistory = computed (() => {
                const savedGames = parseSavedGames()
                if (!savedGames) {
                    return
                }
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
                return savedFrames
            })

            /**
             * Removes any invalid games from localStorage.
             * 
             * Will be updated to remove from DB in the future.
             */
            function removeInvalidGames(){
                const savedGames = parseSavedGames()
                if (!savedGames){
                    // need to update hasGameData to true to avoid displaying "no games" and "corrupt data" messages together
                    hasGameData.value = true
                    hasCorruptedData.value = true
                    return
                }
                // remove invalid games from list of saved games via filter
                const cleanedGames = savedGames.filter((game, i) => !invalidGames.value.includes(i))
                localStorage.setItem('completeGames', JSON.stringify(cleanedGames))
                invalidGames.value.length = 0
            }

            /**
             * Simple helper function to parse saved game data.
             * Handles corrupt save data by updating state variables.
             * @returns {Array|null} - Parsed saved game data, or null if invalid JSON syntax.
             */
            function parseSavedGames(){
                try {
                    return JSON.parse(localStorage.getItem('completeGames'))
                } catch (error){
                    hasGameData.value = true
                    hasCorruptedData.value = true
                    return null
                }
            }

            /**
             * Recovers from corrupted save data by removing all save data.
             * 
             * Once DB is in place, will be able to recover more gracefully.
             */
            function resetGames(){
                localStorage.removeItem('completeGames')
                hasCorruptedData.value = false
                hasGameData.value = false
            }
            return {
                hasGameData,
                gameHistory,
                invalidGames,
                hasCorruptedData,
                displayRoll,
                removeInvalidGames,
                resetGames
            }
        }
    }
</script>