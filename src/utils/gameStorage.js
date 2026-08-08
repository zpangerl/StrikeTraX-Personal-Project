/**
 * Loads a partial game from localStorage, if it exists.
 * @returns {number[]|null} - Partial throws array if it exists, null if not.
 */
export function loadPartialGame(){
    const partialGame = localStorage.getItem('throws')
    if (partialGame === null) return null
    return JSON.parse(partialGame)
}

/**
 * Saves a partial game to localStorage.
 * @param {number[]} throwsArray - The current game's partial throws array.
 */
export function savePartialGame(throwsArray){
    localStorage.setItem('throws', JSON.stringify(throwsArray))
}

/**
 * Clears a partial game from localStorage.
 */
export function clearPartialGame(){
    localStorage.removeItem('throws')
}

/**
 * Loads all completed games from localStorage, if any exist.
 * @returns {Object[]|null} - Array of saved game objects, including a date and a throws array for each, or null if none exist.
 */
export function loadCompleteGames(){
    const completeGames = localStorage.getItem('completeGames')
    if (completeGames === null) return null
    return JSON.parse(completeGames)
}

/**
 * Saves all completed games to localStorage.
 * @param {Object[]} games - Array of saved game objects, including a date and throws array for each.
 */
export function saveCompleteGames(games){
    localStorage.setItem('completeGames', JSON.stringify(games))
}

/**
 * Clears all completed games from localStorage.
 */
export function clearCompleteGames(){
    localStorage.removeItem('completeGames')
}