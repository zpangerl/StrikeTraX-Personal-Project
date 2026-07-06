<template>
  <div class="text-center mt-3 pt-4">
    <h1 class="display-1" style="color: red;"><strong>Bowling Score Tracker</strong></h1>
    <p style="color: red">Landing Page</p>
  </div>
  <div class="d-flex justify-content-center">
    <div>
      <p>Frame: {{ currentFrame }}</p>
      <p>Roll: {{ currentRoll }}</p>
      <p>Scores: {{ throws }}</p>
      <p>Total Score: {{ total }}</p>
      <select v-model.number="rollDropdown">
        <option v-for="n in pins" :key="n - 1" :value="n - 1">{{ n - 1 }}</option>
        <option :value="remainingPins">{{ strikeOrSpare }}</option>
      </select>
      <button @click="handleSubmit" :disabled="rollDropdown === ''">Submit</button>
    </div>
  </div>
</template>

<script>
  import { ref, computed, watch } from 'vue'
  export default {
    setup(){

      var total = ref(0)
      var currentFrame = ref(parseInt(localStorage.getItem('currentFrame')) || 1)
      var currentRoll = ref(parseInt(localStorage.getItem('currentRoll')) || 1)
      var firstRoll = null
      var secondRoll = null
      var throws = ref([])
      var frames = []
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
            frames.push({ frame: currentFrame.value, roll1: null, roll2: null, currentTotal: null })
            firstRoll = rollDropdown.value
            throws.value.push(firstRoll)
            frames[currentFrame.value - 1].roll1 = firstRoll
            rollDropdown.value = ''
            if (firstRoll === 10){
              calculateScore(throws.value)
              firstRoll = null
              remainingPins.value = 10
              currentFrame.value++
              return
            }
            remainingPins.value = computeSecondRoll()
            currentRoll.value++
            calculateScore(throws.value)
            return
          }
          else{
            throws.value.push(rollDropdown.value)
            frames[currentFrame.value - 1].roll2 = secondRoll
            calculateScore(throws.value)
            rollDropdown.value = ''
            firstRoll = null
            currentRoll.value = 1
            currentFrame.value++
            remainingPins.value = 10
            resetPins()
            return
          }
        }
        else if (currentFrame.value === 10){
          var isStrikeOrSpare = false
          if (currentRoll.value === 1){
            frames.push({ frame: currentFrame.value, roll1: null, roll2: null, roll3: null, currentTotal: null })
            firstRoll = rollDropdown.value
            throws.value.push(firstRoll)
            frames[currentFrame.value - 1].roll1 = firstRoll
            rollDropdown.value = ''
            if (firstRoll === 10){
              isStrikeOrSpare = true
              remainingPins.value = 10
              currentRoll.value++
              calculateScore(throws.value)
              return
            }
            remainingPins.value = computeSecondRoll()
            currentRoll.value++
            calculateScore(throws.value)
            return
          }
          else if (currentRoll.value === 2){
            secondRoll = rollDropdown.value
            throws.value.push(secondRoll)
            rollDropdown.value = ''
            if (firstRoll === 10){
              if (secondRoll === 10){
                remainingPins.value = 10
                currentRoll.value++
                calculateScore(throws.value)
                return
              }
              remainingPins.value = computeThirdRoll()
              currentRoll.value++
              calculateScore(throws.value)
              return
            }
            if (secondRoll === remainingPins.value){
              isStrikeOrSpare = true
              currentRoll.value++
              remainingPins.value = 10
              calculateScore(throws.value)
              resetPins()
              return
            }
            else {
              frames[currentFrame.value - 1].roll2 = secondRoll
              calculateScore(throws.value)
              newGame()
              return
            }
          }
          else if (currentRoll.value == 3){
            throws.value.push(rollDropdown.value)
            frames[currentFrame.value - 1].roll3 = rollDropdown.value
            calculateScore(throws.value)
            rollDropdown.value = ''
            newGame()
            return
          }
        }
        else if (currentFrame.value > 10){
          alert("Game Over, final score is " + total.value)
        }
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
            frames[currentFrame - 1].currentTotal = currentTotal
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
            frames[currentFrame - 1].currentTotal = currentTotal
            currentThrow++
          }
          else{
            totalPinsThisFrame += nextThrow
            currentTotal += nextThrow
            frames[currentFrame - 1].currentTotal = currentTotal
            currentThrow++
          }
          if (((currentThrow > 2 || totalPinsThisFrame === 10) && currentFrame !== 10)){
            currentThrow = 1
            frames[currentFrame - 1].currentTotal = currentTotal
            currentFrame++
            totalPinsThisFrame = 0
          }
          throwsIter++
        }
        total.value = currentTotal
      }

      function newGame(){
        alert("Game Over, final score is " + total.value)
        currentFrame.value = 1
        currentRoll.value = 1
        remainingPins.value = 10
        firstRoll = null
        secondRoll = null
        throws.value.length = 0
        frames.legnth = 0
        total.value = 0
        resetPins()
      }

      function gameOver(){

      }

      return {
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
        computeSecondRoll,
        computeThirdRoll,
        handleSubmit,
        newGame,
        gameOver,
      }
    }
  }
</script>

<style>
    body { background-color:  darkslategrey; }
</style>