//   CHUCK UMAP BROWSER (FEATURE COLLECTOR EDITION)


// 1. CONFIGURATION
"/Users/coltonarnold/Desktop/corpse/" => string SOUND_DIR;   

// Analysis Settings
1024 => int FFT_SIZE;
20   => int MFCC_COEFFS;
10   => int MEL_FILTERS;
3    => int K_NEIGHBORS; // Low neighbors for small dataset (32 sounds)

// PHYSICS TUNING 
0.01 => float REPULSION_FORCE;   // Weak push
0.05  => float ATTRACTION_FORCE;  // Strong pull
0.01  => float CENTER_GRAVITY;    // Gentle center pull
0.40  => float DAMPING;           // Muddy friction (stops flying)

// 2. ANALYSIS NETWORK
SndBuf loader => FFT fft;
FeatureCollector combo => blackhole; // The collector object

// Connect features to the collector
fft =^ Centroid centroid =^ combo;
fft =^ Flux flux =^ combo;
fft =^ RMS rms =^ combo;
fft =^ MFCC mfcc =^ combo;

// Configure UAna objects
FFT_SIZE => fft.size;
Windowing.hann(FFT_SIZE) => fft.window;
mfcc.numCoeffs(MFCC_COEFFS);
mfcc.numFilters(MEL_FILTERS);

// Trigger one upchuck to calculate total dimensions
combo.upchuck();
combo.fvals().size() => int NUM_DIMENSIONS;
<<< "Feature Vector Size:", NUM_DIMENSIONS >>>;

// 3. VISUALIZATION SETUP
GWindow.title("ChucK UMAP (FeatureCollector)");
GG.scene().backgroundColor( @(0.1, 0.1, 0.1) );
GG.camera().pos( @(0, 0, 25) ); 
GG.camera().lookAt( @(0, 0, 0) );

SndBuf player => dac; // For playback

// Data Structures
string filenames[0];          
float feature_matrix[0][0];   
float pos_x[0];               
float pos_y[0];               
float vel_x[0];               
float vel_y[0];               
GSphere dots[0];              

// 4. PHASE 1: EXTRACT FEATURES
<<< "STEP 1: ANALYZING WITH FEATURE COLLECTOR " >>>;

FileIO dir;
dir.open( SOUND_DIR );
dir.dirList() @=> string files[];

if( files.cap() == 0 ) {
    <<< "ERROR: No files found in", SOUND_DIR >>>;
    me.exit(); 
}

for( 0 => int f; f < files.cap(); f++ )
{
    SOUND_DIR + files[f] => string path;
    if( path.find(".wav") == -1 && path.find(".aiff") == -1 ) continue;

    // Load file
    path => loader.read;
    loader.samples() => int len;
    if( len == 0 ) continue;
    
    // Accumulators for averaging
    float feature_sum[NUM_DIMENSIONS];
    0 => float count;

    // FAST ANALYSIS LOOP
    // Instead of waiting for time to pass, we scrub through the file
    for( 0 => int i; i < len; FFT_SIZE +=> i ) 
    {
        i => loader.pos; // Move playhead
        combo.upchuck(); // Force analysis calculation
        
        // Add current frame features to sum
        for( 0 => int d; d < NUM_DIMENSIONS; d++ )
        {
            combo.fval(d) +=> feature_sum[d];
        }
        1 +=> count;
    }
    
    // Calculate Average
    float avg_features[NUM_DIMENSIONS];
    for( 0 => int d; d < NUM_DIMENSIONS; d++ ) 
    {
        if( count > 0 ) feature_sum[d] / count => avg_features[d];
    }
    
    // Store Data
    feature_matrix << avg_features;
    filenames << path;
    
    // Create Dot
    pos_x << Math.random2f(-1, 1); 
    pos_y << Math.random2f(-1, 1);
    vel_x << 0.0;
    vel_y << 0.0;
    
    GSphere s;
    s --> GG.scene(); 
    0.3 => s.sca;
    s.mat( FlatMaterial m );
    m.color( @(1, 1, 1) );
    dots << s;
    
    <<< "Analyzed:", files[f] >>>;
}

filenames.cap() => int NUM_POINTS;
<<< "Total Sounds Analyzed:", NUM_POINTS >>>;

// 5. PHASE 2: KNN GRAPH
<<< "STEP 2: BUILDING GRAPH " >>>;
KNN knn;
knn.train( feature_matrix );
int neighbors[NUM_POINTS][K_NEIGHBORS];

for( 0 => int i; i < NUM_POINTS; i++ ) {
    int results[K_NEIGHBORS];
    knn.search( feature_matrix[i], K_NEIGHBORS, results );
    for( 0 => int k; k < K_NEIGHBORS; k++ ) results[k] => neighbors[i][k];
}

// 6. PHASE 3: PHYSICS VIZ LOOP
<<< "STEP 3: RUNNING VIZ" >>>;
int last_played_idx; -1 => last_played_idx;

while( true )
{
    // A. PHYSICS
    for( 0 => int i; i < NUM_POINTS; i++ )
    {
        // 1. Gravity
        -pos_x[i] * CENTER_GRAVITY +=> vel_x[i];
        -pos_y[i] * CENTER_GRAVITY +=> vel_y[i];

        // 2. Repulsion
        for( 0 => int j; j < NUM_POINTS; j++ )
        {
            if( i == j ) continue;
            pos_x[i] - pos_x[j] => float dx;
            pos_y[i] - pos_y[j] => float dy;
            Math.hypot(dx, dy) => float dist;
            if( dist < 0.1 ) 0.1 => dist; 
            
            (REPULSION_FORCE / (dist * dist)) => float force;
            (dx / dist) * force +=> vel_x[i];
            (dy / dist) * force +=> vel_y[i];
        }

        // 3. Attraction
        for( 0 => int k; k < K_NEIGHBORS; k++ )
        {
            neighbors[i][k] => int neighbor_idx;
            pos_x[neighbor_idx] - pos_x[i] => float dx;
            pos_y[neighbor_idx] - pos_y[i] => float dy;
            dx * ATTRACTION_FORCE +=> vel_x[i];
            dy * ATTRACTION_FORCE +=> vel_y[i];
        }
    }
    
    // B. UPDATE (WITH CLAMPING)
    0.1 => float MAX_SPEED;
    for( 0 => int i; i < NUM_POINTS; i++ )
    {
        vel_x[i] * DAMPING => vel_x[i];
        vel_y[i] * DAMPING => vel_y[i];

        if( vel_x[i] > MAX_SPEED ) MAX_SPEED => vel_x[i];
        if( vel_x[i] < -MAX_SPEED ) -MAX_SPEED => vel_x[i];
        if( vel_y[i] > MAX_SPEED ) MAX_SPEED => vel_y[i];
        if( vel_y[i] < -MAX_SPEED ) -MAX_SPEED => vel_y[i];

        vel_x[i] +=> pos_x[i];
        vel_y[i] +=> pos_y[i];
        dots[i].pos( @(pos_x[i], pos_y[i], 0) );
    }
    
    // C. MOUSE
    GWindow.mousePos() => vec2 mouse; 
    GG.windowWidth() => float winW;
    GG.windowHeight() => float winH;
    ((mouse.x - winW/2) / 25.0) => float mouseWorldX; 
    ((winH/2 - mouse.y) / 25.0) => float mouseWorldY; 

    int closest_idx;
    0.5 => float min_dist;
    -1 => closest_idx;

    for( 0 => int i; i < NUM_POINTS; i++ )
    {
        Math.hypot( pos_x[i] - mouseWorldX, pos_y[i] - mouseWorldY ) => float d;
        if( d < 1.0 && d < min_dist ) { d => min_dist; i => closest_idx; }
        dots[i].mat() $ FlatMaterial @=> FlatMaterial m;
        m.color( @(1, 1, 1) );
    }
    
    if( closest_idx != -1 )
    {
        dots[closest_idx].mat() $ FlatMaterial @=> FlatMaterial m;
        m.color( @(1, 0, 0) );
        if( closest_idx != last_played_idx ) {
            closest_idx => last_played_idx;
            filenames[closest_idx] => player.read;
            0 => player.pos;
        }
    } else { -1 => last_played_idx; }

    GG.nextFrame() => now;
}