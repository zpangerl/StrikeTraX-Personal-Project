<template>
    <div class="text-center mt-3 pt-4">
        <h1 class="display-1" style="color: black"><strong>Game History</strong></h1>
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
    import { displayRoll, calculateScore, initializeFrames, validateThrow } from '../utils/scoring.js'
    export default {
        setup(){
            const invalidGames = []

            const gameHistory = computed (() => {
                const savedGames = JSON.parse(localStorage.getItem('completeGames'))
                if (savedGames === null) {
                    alert("No saved games!")
                    return
                }
                const savedFrames = []
                for (let i = savedGames.length - 1; i >= 0; i--){
                    const calculateResult = calculateScore(savedGames[i].throws)
                    if (calculateResult.isValid === false){
                        invalidGames.push(i)
                        continue
                    }
                    const preparedGame = {
                        date: savedGames[i].date,
                        frames: calculateResult.frames
                    }
                    savedFrames.push(preparedGame)
                }
                return savedFrames
            })
            return {
                gameHistory,
                invalidGames,
                displayRoll,
            }
        }
    }
</script>