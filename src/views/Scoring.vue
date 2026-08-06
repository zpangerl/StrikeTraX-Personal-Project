<template>
  <div class="text-center mt-3 pt-4">
    <h1 class="display-5"><strong>Log Game</strong></h1>
  </div>
  <div class="d-flex justify-content-center">
    <div>
      <p>Frame: {{ currentFrame }}</p>
      <p>Roll: {{ currentRoll }}</p>
      <select class="form-select" v-model.number="rollDropdown" v-if="!isEndOfGame">
        <option v-for="n in pins" :key="n - 1" :value="n - 1">{{ n - 1 }}</option>
        <option :value="remainingPins">{{ strikeOrSpare }}</option>
      </select>
      <button class="btn btn-primary" @click="handleSubmit" :disabled="rollDropdown === ''" v-if="!isEndOfGame">Submit</button>
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
    <p class="display-6" v-if="isEndOfGame">Total Score: {{ total }}</p>
  </div>
  <div class="d-flex justify-content-center">
    <button class="btn btn-danger" @click="newGame" v-if="isEndOfGame">Reset Without Saving</button>
    <!--Need to add a new function for the button below that logs the game in localStorage for now, DB later, and then resets-->
    <button class="btn btn-primary" @click="saveGame" v-if="isEndOfGame">Log Game</button>
  </div>
</template>

<script>
  import { ref, computed } from 'vue'
  import { displayRoll, calculateScore, initializeFrames, validateThrow } from '../utils/scoring'
  export default {
    setup(){

      const isEndOfGame = ref(false)
      const total = ref(0)
      const currentFrame = ref(1)
      const currentRoll = ref(1)
      let firstRoll = null
      let secondRoll = null
      let throws = []
      const frames = ref([])
      frames.value = initializeFrames()

      const rollDropdown = ref('')

      const pins = ref([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
      const remainingPins = ref(10)

      const loadThrows = localStorage.getItem('throws')

      if (loadThrows !== null){
        loadGame()
      }
      else if (currentFrame.value < 1 || currentFrame.value > 10) newGame()

      const strikeOrSpare = computed (() => {
        if (currentFrame.value !== 10 && currentRoll.value === 1) return 'X'
        else if (currentFrame.value !== 10 && currentRoll.value === 2) return '/'
        else if (currentFrame.value === 10 && currentRoll.value === 1) return 'X'
        else if (currentFrame.value === 10 && currentRoll.value === 2 && firstRoll === 10) return 'X'
        else if (currentFrame.value === 10 && currentRoll.value === 2 && firstRoll !== 10) return '/'
        else if (currentFrame.value === 10 && currentRoll.value === 3 && remainingPins.value === 10) return 'X'
        else if (currentFrame.value === 10 && currentRoll.value === 3 && remainingPins.value !== 10) return '/'
        else return 'error'
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
        let throwAdded = true
        if (currentFrame.value > 0 && currentFrame.value < 10){
          if (currentRoll.value === 1){
            firstRoll = rollDropdown.value
            throwAdded = addThrow(firstRoll)
            if (!throwAdded) return
            if (firstRoll === 10){
              firstRoll = null
              remainingPins.value = 10
              currentFrame.value++
              return
            }
            remainingPins.value = computeSecondRoll()
            currentRoll.value++
            return
          }
          else{
            throwAdded = addThrow(rollDropdown.value)
            if (!throwAdded) return
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
            throwAdded = addThrow(firstRoll)
            if (!throwAdded) return
            if (firstRoll === 10){
              remainingPins.value = 10
              currentRoll.value++
              return
            }
            remainingPins.value = computeSecondRoll()
            currentRoll.value++
            return
          }
          else if (currentRoll.value === 2){
            secondRoll = rollDropdown.value
            throwAdded = addThrow(secondRoll)
            if (!throwAdded) return
            if (firstRoll === 10){
              if (secondRoll === 10){
                remainingPins.value = 10
                currentRoll.value++
                return
              }
              remainingPins.value = computeThirdRoll()
              currentRoll.value++
              return
            }
            if (secondRoll === remainingPins.value){
              currentRoll.value++
              remainingPins.value = 10
              resetPins()
              return
            }
            else {
              isEndOfGame.value = true
              return
            }
          }
          else if (currentRoll.value === 3){
            throwAdded = addThrow(rollDropdown.value)
            if (!throwAdded) return
            isEndOfGame.value = true
            return
          }
        }
      }

      function addThrow(newThrow){
        throws.push(newThrow)
        rollDropdown.value = ''
        savePartialGame(throws)
        const scoreJSON = calculateScore(throws)
        if (!scoreJSON.isValid || scoreJSON.frames === null || scoreJSON.total === null){
          // for now, will update later to actually resolve back to previous throw/frame/whatever if invalid
          newGame()
          return false
        }
        else {
          frames.value = scoreJSON.frames
          total.value = scoreJSON.total
          return true
        }
      }

      function savePartialGame(throwsArray){
        localStorage.setItem('throws', JSON.stringify(throwsArray))
      }

      function newGame(){
        currentFrame.value = 1
        currentRoll.value = 1
        remainingPins.value = 10
        firstRoll = null
        secondRoll = null
        throws.length = 0
        frames.value.length = 0
        localStorage.removeItem('throws')
        frames.value = initializeFrames()
        total.value = 0
        resetPins()
        isEndOfGame.value = false
      }

      function saveGame(){
        let savedGames = null
        try {
          savedGames = JSON.parse(localStorage.getItem('completeGames'))
        } catch (error){
          alert("Corrupted game data, game could not be saved")
          newGame()
          return
        }
        const currDate = new Date().toISOString()
        let storeGames = []
        const newSave = {
          date: currDate,
          throws: null
        }
        if (savedGames === null){
          newSave.throws = throws
          storeGames.push(newSave)
          localStorage.setItem('completeGames', JSON.stringify(storeGames))
        }
        else {
          newSave.throws = throws
          savedGames.push(newSave)
          localStorage.setItem('completeGames', JSON.stringify(savedGames))
        }
        newGame()
      }

      function loadGame(){
        if (localStorage.getItem('throws') !== null){
          // load, parse, and validate throws array
          try{
          throws = JSON.parse(localStorage.getItem('throws'))
          } catch (error){
            newGame()
            alert("Invalid save data, starting new game")
            return
          }
          currentFrame.value = 1
          currentRoll.value = 1
          let throwsIter = 0
          let firstRollLoad = null
          let secondRollLoad = null
          let thirdRollLoad = null
          let remainingPinsLoad = 10
          while (throwsIter < throws.length){
            if (currentFrame.value > 0 && currentFrame.value < 10){
              if (currentRoll.value === 1){
                firstRollLoad = throws[throwsIter]
                if (!validateThrow(firstRollLoad, remainingPinsLoad)){
                  newGame()
                  return
                }
                throwsIter++
                if (firstRollLoad === 10){
                  //handle strike
                  currentFrame.value++
                  continue
                }
                else {
                  remainingPinsLoad = 10 - firstRollLoad
                  currentRoll.value++
                }
              }
              else {
                secondRollLoad = throws[throwsIter]
                if (!validateThrow(secondRollLoad, remainingPinsLoad)){
                  newGame()
                  return
                }
                throwsIter++
                firstRollLoad = null
                currentRoll.value = 1
                currentFrame.value++
                remainingPinsLoad = 10
              }
            }
            else if (currentFrame.value === 10){
              if (currentRoll.value === 1){
                firstRollLoad = throws[throwsIter]
                if (!validateThrow(firstRollLoad, remainingPinsLoad)){
                  newGame()
                  return
                }
                throwsIter++
                currentRoll.value++
                if (firstRollLoad !== 10){
                  remainingPinsLoad = 10 - firstRollLoad
                }
                else {
                  remainingPinsLoad = 10
                }
                continue
              }
              else if (currentRoll.value === 2){
                secondRollLoad = throws[throwsIter]
                if (!validateThrow(secondRollLoad, remainingPinsLoad)){
                  newGame()
                  return
                }
                throwsIter++
                if (firstRollLoad === 10){
                  if (secondRollLoad === 10){
                    currentRoll.value++
                    continue
                  }
                  remainingPinsLoad = remainingPinsLoad - secondRollLoad
                  currentRoll.value++
                  continue
                }
                if (secondRollLoad === remainingPinsLoad){
                  currentRoll.value++
                  remainingPinsLoad = 10
                  continue
                }
                else{
                  if (throwsIter !== throws.length){
                    newGame()
                    return
                  }
                  isEndOfGame.value = true
                  break
                }
              }
              else if (currentRoll.value === 3){
                thirdRollLoad = throws[throwsIter]
                throwsIter++
                if (!validateThrow(thirdRollLoad, remainingPinsLoad)){
                  newGame()
                  return
                }
                if (throwsIter !== throws.length){
                  newGame()
                  return
                }
                isEndOfGame.value = true
                break
              }
            }
          }
          remainingPins.value = remainingPinsLoad
          pins.value.length = 0
          for (let i = 1; i <= remainingPins.value; i++){
            pins.value.push(i)
          }
          firstRoll = firstRollLoad
          secondRoll = secondRollLoad
          const scoreJSON = calculateScore(throws)
          if (!scoreJSON.isValid || scoreJSON.frames === null){
          // for now, will update later to actually resolve back to previous throw/frame/whatever if invalid
            newGame()
            return
          }
          else {
            frames.value = scoreJSON.frames
            total.value = scoreJSON.total
          }
        }
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
        handleSubmit,
        displayRoll,
        newGame,
        saveGame
      }
    }
  }
</script>