const max = require('max-api');

// --- THE CONFIGURATION ---
// 1. Hidden States (The "Moods")
const states = ['CHILL', 'TENSE'];

// 2. Vocabulary (The MIDI Notes)
// Chill notes (Pentatonic C): 60(C), 62(D), 64(E), 67(G)
// Tense notes (Diminished/Cluster): 71(B), 72(C), 73(C#), 74(D)
const vocabulary = [60, 62, 64, 67, 71, 72, 73, 74];

// 3. Transition Matrix (Probability of switching states)
// [Probability to go to Chill, Probability to go to Tense]
const transitions = [
    [0.9, 0.1], // If currently CHILL: 90% stay Chill, 10% switch to Tense
    [0.2, 0.8]  // If currently TENSE: 20% switch to Chill, 80% stay Tense
];

// 4. Emission Matrix (Probability of playing a specific note)
// Each row must add up to 1.0. 
// Columns correspond to the 'vocabulary' list above.
const emissions = [
    // CHILL State: Mostly plays low notes (60-67), never plays high notes
    [0.3, 0.3, 0.3, 0.1, 0.0, 0.0, 0.0, 0.0], 
    
    // TENSE State: Mostly plays high notes (71-74), rarely plays low
    [0.0, 0.0, 0.0, 0.05, 0.25, 0.3, 0.2, 0.2] 
];




let currentStateIndex = 0; // Start in "Chill" (Index 0)

function weightedRandom(probs) {
    let sum = probs.reduce((a, b) => a + b, 0); //should equal to 1
    let r = Math.random() * sum; //
    for (let i = 0; i < probs.length; i++) {
        r -= probs[i];
        if (r <= 0) return i;
    }
    return 0; // Fallback
}

max.addHandlers({
    step: () => {
        // 1. Handle Transition (Move to next State)
        let currentTransProbs = transitions[currentStateIndex]; //what state are we looking at
        currentStateIndex = weightedRandom(currentTransProbs); //What state are we going to
        
        // 2. Handle Emission (Pick a note based on new State)
        let currentEmissionProbs = emissions[currentStateIndex]; //Which emmisions set are we looking at
        let noteIndex = weightedRandom(currentEmissionProbs); //Pick a note based on emmisions probability
        let note = vocabulary[noteIndex];
        
        // 3. Output
        max.outlet("result", states[currentStateIndex], note);
    }
});