const max = require('max-api');

// --- DEFAULT CONFIGURATION ---
let states = ['CHILL', 'TENSE'];
let vocabulary = [60, 62, 64, 67, 71, 72, 73, 74];
let transitions = [[0.9, 0.1], [0.2, 0.8]];
let emissions = [
    [0.3, 0.3, 0.3, 0.1, 0.0, 0.0, 0.0, 0.0], 
    [0.0, 0.0, 0.0, 0.05, 0.25, 0.3, 0.2, 0.2] 
];

let currentStateIndex = 0; 

// --- HELPER: UPDATE FUNCTION ---
// We extract this so we can call it from multiple handlers
function updateConfig(content) {
    if (!content) return;

    // Check for keys (using lowercase to be safe)
    if (content.states) states = content.states;
    if (content.vocabulary) vocabulary = content.vocabulary;
    if (content.transitions) transitions = content.transitions;
    if (content.emissions) emissions = content.emissions;
    
    // Reset index to prevent crashes
    currentStateIndex = 0; 
    
    max.post("SUCCESS: Configuration updated.");
    max.post("Current States: " + JSON.stringify(states));
}

// --- HELPER: RANDOM ---
function weightedRandom(probs) {
    if (!probs || probs.length === 0) return 0;
    let sum = probs.reduce((a, b) => a + b, 0);
    let r = Math.random() * sum;
    for (let i = 0; i < probs.length; i++) {
        r -= probs[i];
        if (r <= 0) return i;
    }
    return 0;
}

// --- MAX HANDLERS ---
max.addHandlers({

    step: () => {
        try {
            if (!transitions[currentStateIndex]) currentStateIndex = 0;

            // 1. Transition
            currentStateIndex = weightedRandom(transitions[currentStateIndex]); 

            // 2. Emission
            let currentEmissionProbs = emissions[currentStateIndex]; 
            if (!currentEmissionProbs) return; 

            let noteIndex = weightedRandom(currentEmissionProbs); 
            let note = vocabulary[noteIndex];

            // 3. Output
            max.outlet("result", states[currentStateIndex], note);
        } catch (e) {
            max.post("Error in step: " + e.message);
        }
    },

    // --- HANDLER 1: "dictionary" (Standard API) ---
    [max.DICT_IDENTIFIER]: async (id) => {
        max.post("Received 'dictionary' message.");
        let content = await max.getDict(id);
        updateConfig(content);
    },

    // --- HANDLER 2: "dict" (The one triggering your error) ---
    dict: async (data) => {
        max.post("Received 'dict' message.");
        
        let content = data;

        // If 'data' is just a name (string), we need to fetch the dict content
        if (typeof data === 'string') {
             max.post("It is a name, fetching content...");
             content = await max.getDict(data);
        } 
        // If 'data' is already an object, we use it directly
        else {
             max.post("It is a raw object, applying directly...");
        }

        updateConfig(content);
    }
});