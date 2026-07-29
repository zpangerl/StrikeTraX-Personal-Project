export function displayRoll(frame, rollNum){
    const roll = frame[`roll${rollNum}`]
    if (roll === null) return ''
    if (roll === 10) return 'X'
    else if (frame.frame === 10 && roll === 10) return 'X'
    else if (rollNum === 2 && frame.roll1 + roll === 10 && frame.roll1 !== 10) return '/'
    else if (rollNum === 3 && frame.roll2 + roll === 10 && frame.roll2 !== 10) return '/'
    else return roll
}

export function calculateScore(throwsArray){
    var throwsIter = 0
    var currentThrow = 1
    var currentFrame = 1
    var totalPinsThisFrame = 0
    var currentTotal = 0
    let gameFrames = initializeFrames()
    const returnJSON = {
      frames: null,
      isValid: true,
      currThrow: 1,
      currFrame: 1,
      pinsLeft: 10,
      total: null
    }

    while (throwsIter < throwsArray.length){
      var nextThrow = throwsArray[throwsIter]
      if (!validateThrow(nextThrow, 10 - totalPinsThisFrame)){
        returnJSON.isValid = false
        return returnJSON
      }
      //if (typeof nextThrow !== 'number' || nextThrow < 0 || nextThrow > (10 - totalPinsThisFrame)){
      //  returnJSON.isValid = false
      //  return returnJSON
      //}
      if (currentThrow === 1 && nextThrow === 10 && currentFrame !== 10){
        if (throwsIter + 2 >= throwsArray.length) {
          if (throwsArray[throwsIter + 1] !== undefined){
            gameFrames[currentFrame].roll1 = throwsArray[throwsIter + 1]
          }
          gameFrames[currentFrame - 1].roll1 = nextThrow
          returnJSON.frames = gameFrames
          returnJSON.currThrow = currentThrow
          returnJSON.currFrame = currentFrame
          returnJSON.pinsLeft = 10 - totalPinsThisFrame
          returnJSON.total = currentTotal
          return returnJSON
        }
        totalPinsThisFrame += nextThrow
        currentTotal += nextThrow
        currentTotal += throwsArray[throwsIter + 1]
        currentTotal += throwsArray[throwsIter + 2]
        gameFrames[currentFrame - 1].roll1 = nextThrow
        gameFrames[currentFrame - 1].currentTotal = currentTotal
        currentThrow++
      }
      else if (currentThrow === 2 && nextThrow === (10 - totalPinsThisFrame) && currentFrame !== 10){
        if (throwsIter + 1 >= throwsArray.length) {
          gameFrames[currentFrame - 1].roll2 = nextThrow
          gameFrames[currentFrame - 1].currentTotal = null
          returnJSON.frames = gameFrames
          returnJSON.currThrow = currentThrow
          returnJSON.currFrame = currentFrame
          returnJSON.pinsLeft = 10 - totalPinsThisFrame
          returnJSON.total = currentTotal
          return returnJSON
        }
        totalPinsThisFrame += nextThrow
        currentTotal += nextThrow
        currentTotal += throwsArray[throwsIter + 1]
        gameFrames[currentFrame - 1].roll2 = nextThrow
        gameFrames[currentFrame - 1].currentTotal = currentTotal
        currentThrow++
      }
      else if (currentFrame === 10){
        if (currentThrow === 1){
          if (nextThrow !== 10){
            totalPinsThisFrame += nextThrow
          }
          else totalPinsThisFrame = 0
        }
        else if (currentThrow === 2){
          if (gameFrames[currentFrame - 1].roll1 === 10){
            if (nextThrow === 10){
              totalPinsThisFrame = 0
            }
              else {
                totalPinsThisFrame += nextThrow
              }
            }
            else{
              if (nextThrow === (10 - totalPinsThisFrame)){
                totalPinsThisFrame = 0
              }
              else{
                totalPinsThisFrame = 10
                currentTotal += nextThrow
                gameFrames[currentFrame - 1].roll2 = nextThrow
                gameFrames[currentFrame - 1].currentTotal = currentTotal
                currentThrow++
                break
              }
            }
          }
          else if (currentThrow === 3){
            currentTotal += nextThrow
            gameFrames[currentFrame - 1].roll3 = nextThrow
            gameFrames[currentFrame - 1].currentTotal = currentTotal
            currentThrow++
            break
          }
          currentTotal += nextThrow
          gameFrames[currentFrame - 1][`roll${currentThrow}`] = nextThrow
          gameFrames[currentFrame - 1].currentTotal = currentTotal
          currentThrow++
        }
        else{
          totalPinsThisFrame += nextThrow
          currentTotal += nextThrow
          gameFrames[currentFrame - 1][`roll${currentThrow}`] = nextThrow
          if (currentThrow != 1){
            gameFrames[currentFrame - 1].currentTotal = currentTotal
          }
          currentThrow++
        }
        if (((currentThrow > 2 || totalPinsThisFrame === 10) && currentFrame !== 10)){
          currentThrow = 1
          gameFrames[currentFrame - 1].currentTotal = currentTotal
          currentFrame++
          totalPinsThisFrame = 0
        }
        throwsIter++
      }
      returnJSON.total = currentTotal
      returnJSON.currThrow = currentThrow
      returnJSON.currFrame = currentFrame
      returnJSON.pinsLeft = 10 - totalPinsThisFrame
      returnJSON.frames = gameFrames
      return returnJSON
}

export function initializeFrames(){
    let framesArr = []
    for (var i = 0; i < 9; i++){
      framesArr.push({ frame: i + 1, roll1: null, roll2: null, currentTotal: null })
    }
    framesArr.push({ frame: 10, roll1: null, roll2: null, roll3: null, currentTotal: null })
    return framesArr
}

export function validateThrow(throwVal, pinsVal){
      if (typeof throwVal !== 'number' || throwVal < 0 || throwVal > pinsVal){
        return false
      }
      else return true
      if (throwVal >= 0 && throwVal <= pinsVal){
        return true
      }
      else return false
}