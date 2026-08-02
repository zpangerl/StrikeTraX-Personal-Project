<template>
    <div class="text-center mt-3 pt-4">
        <h1 class="display-1" style="color: black"><strong>Game History</strong></h1>
    </div>
    <div class="d-flex justify-content-center" v-if="!hasGameData">
        <h4 class="display-4" style="color: black">No games to display!</h4>
    </div>
    <div class="d-flex justify-content-center" v-if="invalidGames.length !== 0">
        <h4 class="display-4" style="color: black">{{ invalidGames.length }} games could not be loaded due to invalid data</h4>
        <button @click="removeInvalidGames">Remove Invalid Games</button>
    </div>
    <div class="d-flex align-items-center flex-column">
        <div v-for="(game, i) in gameHistory" :key="i">
            <h3 class="display-1" style="color: black">Game {{ i + 1 }}: {{ new Date(game.date).toLocaleString() }}</h3>
            <div class="scorecard d-flex justify-content-center">
                <div v-for="(frame, j) in game.frames" :key="j" class="frame-wrapper text-center me-2">
                    <div class="frame-number mb-1">{{ j + 1 }}</div>
                    <div class=frame-cell>
                        <div class="roll-boxes">
                            <div class="roll-box">{{ displayRoll(frame, 1) }}</div>
                            <div class="roll-box">{{ displayRoll(frame, 2) }}</div>
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
            const hasGameData = ref(false)

            const gameHistory = computed (() => {
                const savedGames = parseSavedGames()
                if (!savedGames) {
                    return
                }
                const savedFrames = []
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

            function removeInvalidGames(){
                const savedGames = parseSavedGames()
                if (!savedGames){
                    alert("Corrupted data, could not remove invalid games")
                    return
                }
                const cleanedGames = savedGames.filter((game, i) => !invalidGames.value.includes(i))
                localStorage.setItem('completeGames', JSON.stringify(cleanedGames))
                invalidGames.value.length = 0
            }

            function parseSavedGames(){
                try {
                    return JSON.parse(localStorage.getItem('completeGames'))
                } catch (error){
                    alert("Saved games corrupted, could not load")
                    return null
                }
            }
            return {
                hasGameData,
                gameHistory,
                invalidGames,
                displayRoll,
                removeInvalidGames
            }
        }
    }
</script>