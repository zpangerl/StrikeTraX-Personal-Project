<template>
  <div class="text-center mt-3 pt-4">
    <h1 class="display-1" style="color: red;"><strong>Bowling Score Tracker</strong></h1>
    <p style="color: red">Landing Page</p>
  </div>
  <div class="d-flex justify-content-center">
    <div>
      <p>Frame: {{ currentFrame }}</p>
      <p>Roll: {{ currentRoll }}</p>
      <select v-model.number="rollDropdown" v-if="!isEndOfGame">
        <option v-for="n in pins" :key="n - 1" :value="n - 1">{{ n - 1 }}</option>
        <option :value="remainingPins">{{ strikeOrSpare }}</option>
      </select>
      <button @click="handleSubmit" :disabled="rollDropdown === ''" v-if="!isEndOfGame">Submit</button>
    </div>
  </div>
  <div class="d-flex justify-content-center">
    <div class="scorecard d-flex">
      <div v-for="(frame, i) in frames" :key="i" class="frame-wrapper text-center me-2">
        <div class="frame-number mb-1">{{ i + 1 }}</div>
        <div class="frame-cell">
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
  <div class="d-flex justify-content-center">
    <button @click="newGame" v-if="isEndOfGame">Reset Without Saving</button>
    <!--Need to add a new function for the button below that logs the game in localStorage for now, DB later, and then resets-->
    <button @click="newGame" v-if="isEndOfGame">Log Game</button>
  </div>
</template>

<script>
  import { ref, computed, watch } from 'vue'
  export default {
    setup(){

      var isEndOfGame = ref(false)
      var total = ref(0)
      var currentFrame = ref(parseInt(localStorage.getItem('currentFrame')) || 1)
      var currentRoll = ref(parseInt(localStorage.getItem('currentRoll')) || 1)
      var firstRoll = null
      var secondRoll = null
      var throws = []
      var frames = ref([])
      initializeFrames()
      if (currentFrame.value < 1 || currentFrame.value > 10) newGame()

      const rollDropdown = ref('')

      var pins = ref([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
      var remainingPins = ref(10)

      const strikeOrSpare = computed (() => {
        if (currentFrame.value !== 10 && currentRoll.value === 1) return 'X'
        else if (currentFrame.value !== 10 && currentRoll.value === 2) return '/'
        else if (currentFrame.value === 10 && currentRoll.value === 1) return 'X'
        else if (currentFrame.value === 10 && currentRoll.value === 2 && firstRoll === 10) return 'X'
        else if (currentFrame.value === 10 && currentRoll.value === 2 && firstRoll !== 10) return '/'
        else if (currentFrame.value === 10 && currentRoll.value === 3 && remainingPins.value === 10) return 'X'
        else if (currentFrame.value === 10 && currentRoll.value === 3 && remainingPins.value !== 10) return '/'
        else return 'error'
        // handle roll 2 and 3 of frame 10 still
      })

      function computeSecondRoll(){
        const pinsLeft = remainingPins.value - firstRoll
        pins.value.length = 0
        for (let i = 1; i <= pinsLeft; i++){
          pins.value.push(i)
        }
        return pinsLeft
      }

      function computeThirdRoll(){
        const pinsLeft = remainingPins.value - secondRoll
        pins.value.length = 0
        for (let i = 1; i <= pinsLeft; i++){
          pins.value.push(i)
        }
        return pinsLeft
      }

      function resetPins(){
        pins.value.length = 0
        for (let i = 1; i <= 10; i++){
          pins.value.push(i)
        }
      }

      function handleSubmit(){
        if (currentFrame.value > 0 && currentFrame.value < 10){
          if (currentRoll.value === 1){
            firstRoll = rollDropdown.value
            addThrow(firstRoll, "roll1")
            //throws.push(firstRoll)
            //frames.value[currentFrame.value - 1].roll1 = firstRoll
            //rollDropdown.value = ''
            if (firstRoll === 10){
              //calculateScore(throws)
              firstRoll = null
              remainingPins.value = 10
              currentFrame.value++
              return
            }
            remainingPins.value = computeSecondRoll()
            currentRoll.value++
            //calculateScore(throws)
            return
          }
          else{
            addThrow(rollDropdown.value, "roll2")
            //throws.push(rollDropdown.value)
            //frames.value[currentFrame.value - 1].roll2 = rollDropdown.value
            //calculateScore(throws)
            //rollDropdown.value = ''
            firstRoll = null
            currentRoll.value = 1
            currentFrame.value++
            remainingPins.value = 10
            resetPins()
            return
          }
        }
        else if (currentFrame.value === 10){
          if (currentRoll.value === 1){
            firstRoll = rollDropdown.value
            addThrow(firstRoll, "roll1")
            //throws.push(firstRoll)
            //frames.value[currentFrame.value - 1].roll1 = firstRoll
            //rollDropdown.value = ''
            if (firstRoll === 10){
              remainingPins.value = 10
              currentRoll.value++
              //calculateScore(throws)
              return
            }
            remainingPins.value = computeSecondRoll()
            currentRoll.value++
            //calculateScore(throws)
            return
          }
          else if (currentRoll.value === 2){
            secondRoll = rollDropdown.value
            addThrow(secondRoll, "roll2")
            //throws.push(secondRoll)
            //frames.value[currentFrame.value - 1].roll2 = secondRoll
            //rollDropdown.value = ''
            if (firstRoll === 10){
              if (secondRoll === 10){
                remainingPins.value = 10
                currentRoll.value++
                //calculateScore(throws)
                return
              }
              remainingPins.value = computeThirdRoll()
              currentRoll.value++
              //calculateScore(throws)
              return
            }
            if (secondRoll === remainingPins.value){
              currentRoll.value++
              remainingPins.value = 10
              //calculateScore(throws)
              resetPins()
              return
            }
            else {
              //frames.value[currentFrame.value - 1].roll2 = secondRoll
              //calculateScore(throws)
              //Variable for controlling end game state needs to replace
              isEndOfGame.value = true
              return
            }
          }
          else if (currentRoll.value == 3){
            addThrow(rollDropdown.value, "roll3")
            //throws.push(rollDropdown.value)
            //frames.value[currentFrame.value - 1].roll3 = rollDropdown.value
            //calculateScore(throws)
            //rollDropdown.value = ''
            //variable for controlling end game state needs to replace
            isEndOfGame.value = true
            return
          }
        }
      }

      function displayRoll(frame, rollNum){
        const roll = frame[`roll${rollNum}`]
        if (roll === undefined) return ''

        if (roll === 10) return 'X'
        else if (frame.frame === 10 && roll === 10) return 'X'
        else if (rollNum === 2 && frame.roll1 + roll === 10 && frame.roll1 !== 10) return '/'
        else if (rollNum === 3 && frame.roll2 + roll === 10 && frame.roll2 !== 10) return '/'
        else return roll
      }

      function addThrow(newThrow, rollNum){
        throws.push(newThrow)
        frames.value[currentFrame.value - 1][rollNum] = newThrow
        rollDropdown.value = ''
        calculateScore(throws)
      }

      function calculateScore(throwsArray){
        var throwsIter = 0
        var currentThrow = 1
        var currentFrame = 1
        var totalPinsThisFrame = 0
        var currentTotal = 0
        while (throwsIter < throwsArray.length){
          var nextThrow = throwsArray[throwsIter]
          if (currentThrow === 1 && nextThrow === 10 && currentFrame !== 10){
            if (throwsIter + 2 >= throwsArray.length) {
              total.value = currentTotal
              return
            }
            totalPinsThisFrame += nextThrow
            currentTotal += nextThrow
            currentTotal += throwsArray[throwsIter + 1]
            currentTotal += throwsArray[throwsIter + 2]
            frames.value[currentFrame - 1].currentTotal = currentTotal
            currentThrow++
          }
          else if (currentThrow === 2 && nextThrow === (10 - totalPinsThisFrame) && currentFrame !== 10){
            if (throwsIter + 1 >= throwsArray.length) {
              total.value = currentTotal
              return
            }
            totalPinsThisFrame += nextThrow
            currentTotal += nextThrow
            currentTotal += throwsArray[throwsIter + 1]
            frames.value[currentFrame - 1].currentTotal = currentTotal
            currentThrow++
          }
          else{
            totalPinsThisFrame += nextThrow
            currentTotal += nextThrow
            frames.value[currentFrame - 1].currentTotal = currentTotal
            currentThrow++
          }
          if (((currentThrow > 2 || totalPinsThisFrame === 10) && currentFrame !== 10)){
            currentThrow = 1
            frames.value[currentFrame - 1].currentTotal = currentTotal
            currentFrame++
            totalPinsThisFrame = 0
          }
          throwsIter++
        }
        total.value = currentTotal
      }

      function newGame(){
        alert("Game Over, final score is " + frames.value[frames.value.length - 1].currentTotal)
        currentFrame.value = 1
        currentRoll.value = 1
        remainingPins.value = 10
        firstRoll = null
        secondRoll = null
        throws.length = 0
        frames.value.length = 0
        initializeFrames()
        total.value = 0
        resetPins()
        isEndOfGame.value = false
      }

      function initializeFrames(){
        for (var i = 0; i < 9; i++){
          frames.value.push({ frame: i + 1, roll1: null, roll2: null, currentTotal: null })
        }
        frames.value.push({ frame: 10, roll1: null, roll2: null, roll3: null, currentTotal: null })
      }

      return {
        isEndOfGame,
        currentFrame,
        currentRoll,
        firstRoll,
        secondRoll,
        throws,
        frames,
        pins,
        rollDropdown,
        strikeOrSpare,
        remainingPins,
        total,
        addThrow,
        displayRoll,
        computeSecondRoll,
        computeThirdRoll,
        handleSubmit,
        newGame,
        initializeFrames,
      }
    }
  }
</script>

<style>
    body { background-color:  darkslategrey; }
</style>

<style scoped>

  .scorecard {
    overflow-x: auto;
    padding-bottom: 0.5rem;
  }

  .frame-cell {
    position: relative;
    width: 70px;
    height: 70px;
    border: 1px solid #333;
  }

  .roll-boxes {
    position: absolute;
    top: 0;
    right: 0;
    display: flex;
  }

  .roll-box {
    width: 20px;
    height: 20px;
    border-left: 1px solid #333;
    border-bottom: 1px solid #333;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
  }

  .frame-total {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
  }
</style>