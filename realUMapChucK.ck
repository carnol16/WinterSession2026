// =================================================================
//   REAL UMAP: RESPONSIVE VERSION (Fixes Mac "Freeze")
// =================================================================

// 1. CONFIGURATION
"/Users/coltonarnold/Desktop/corpse/" => string AUDIO_DIR;  
64 => int MAX_SAMPLES;       
15 => int N_NEIGHBORS;
500 => int N_EPOCHS;
1.0 => float LEARNING_RATE;
5 => int NEGATIVE_SAMPLES;

// -----------------------------------------------------------------
// 0. GRAPHICS INIT
// -----------------------------------------------------------------
GWindow.windowed(1024, 768);
GWindow.title("UMAP: Loading...");

GG.camera().pos( @(0, 0, 30) );
GG.camera().lookAt( @(0, 0, 0) );

// Loading Spinner
GCube spinner --> GG.scene();
FlatMaterial spinMat;         
spinMat.color( @(1, 0, 0) );  
spinner.mat(spinMat);         
1.0 => spinner.sca;

fun void update_loading_screen() {
    (now / second) * 2.0 => float t; 
    spinner.rot( @(0, t, 0) ); 
    GG.nextFrame() => now;             
}

// -----------------------------------------------------------------
// 2. DATA STRUCTURES
// -----------------------------------------------------------------
class AudioPoint {
    string filename;
    int id;
    float features[0];
    float rho; float sigma; float x; float y;
    SndBuf buf; Pan2 pan;
    
    fun void init(int idx, string f) {
        idx => id; f => filename;
        filename => buf.read; buf.samples() => buf.pos; 0.5 => buf.gain;
    }
    fun void play() {
        buf => pan => dac; 0 => buf.pos; Math.random2f(0.8, 1.2) => buf.rate;
    }
}
AudioPoint points[0];
float distances[MAX_SAMPLES][MAX_SAMPLES];
float graph[MAX_SAMPLES][MAX_SAMPLES]; 

// -----------------------------------------------------------------
// 3. RESPONSIVE ANALYSIS
// -----------------------------------------------------------------
fun void analyze_audio() {
    FileIO dir;
    dir.open(AUDIO_DIR); 
    dir.dirList() @=> string files[]; 
    
    if( files.size() == 0 ) {
        <<< "ERROR: No files in", AUDIO_DIR >>>; return;
    }

    SndBuf analyzer => PoleZero dcblock => FFT fft => blackhole;
    dcblock.blockZero(0.99);
    1024 => fft.size;
    Windowing.hann(1024) => fft.window;
    Centroid centroid =^ fft; RMS rms =^ fft; Flux flux =^ fft; MFCC mfcc =^ fft;
    20 => mfcc.numCoeffs;
    
    0 => int count;
    
    for( 0 => int i; i < files.cap() && count < MAX_SAMPLES; i++ ) {
        files[i] => string filename;
        if( filename.find(".wav") == -1 && filename.find(".aiff") == -1 ) continue;
        
        <<< "Processing [", (count+1), "]:", filename >>>; 
        update_loading_screen(); 
        
        AudioPoint p;
        p.init(count, AUDIO_DIR + filename);
        points << p;
        
        AUDIO_DIR + filename => analyzer.read;
        if( analyzer.samples() == 0 ) continue;

        analyzer.samples() => int len;
        if(len > 10000) 10000 => len; 
        
        float feat_sum[23]; 0 => int frames;
        
        // --- CRITICAL FIX: Yield inside the loop ---
        for(0 => int pos; pos < len; pos + 512) {
            analyzer.pos(pos);
            mfcc.upchuck(); centroid.upchuck(); flux.upchuck(); rms.upchuck();
            centroid.fval(0) +=> feat_sum[0];
            flux.fval(0)     +=> feat_sum[1];
            rms.fval(0)      +=> feat_sum[2];
            for(0=>int k; k<20; k++) mfcc.fval(k) +=> feat_sum[3+k];
            frames++;
            
            // This prevents the Mac "Spinning Wheel"
            if(frames % 20 == 0) GG.nextFrame() => now;
        }
        
        for(0=>int k; k<23; k++) {
            feat_sum[k] / frames => float val;
            if(k==0) Math.log(val+1) => val; 
            p.features << val;
        }
        count++;
    }
}

// -----------------------------------------------------------------
// 4. GRAPH & LAYOUT
// -----------------------------------------------------------------
fun void build_fuzzy_graph() {
    points.size() => int N;
    <<< "--- Building Graph ---" >>>;
    for(0=>int i; i<N; i++) {
        update_loading_screen(); // Keep Mac happy
        100000.0 => float min_d;
        for(0=>int j; j<N; j++) {
            if(i==j) { 0 => distances[i][j]; continue; }
            0.0 => float sum;
            for(0=>int d; d<points[i].features.size(); d++) {
                points[i].features[d] - points[j].features[d] => float diff;
                diff * diff +=> sum;
            }
            Math.sqrt(sum) => float d; d => distances[i][j];
            if(d < min_d) d => min_d;
        }
        min_d => points[i].rho;
    }
    
    Math.log2(N_NEIGHBORS) => float target_entropy;
    
    for(0=>int i; i<N; i++) {
        update_loading_screen(); // Keep Mac happy
        0.001 => float low; 1000.0 => float high; 1.0 => float sigma;
        for(0=>int iter; iter<64; iter++) { 
            (low + high) * 0.5 => sigma;
            0.0 => float p_sum;
            for(0=>int j; j<N; j++) {
                if(i==j) continue;
                distances[i][j] - points[i].rho => float d; if(d<0) 0 => d; 
                Math.exp(-d / sigma) +=> p_sum;
            }
            if(Math.fabs(p_sum - target_entropy) < 0.001) break;
            if(p_sum > target_entropy) sigma => high; else sigma => low;
        }
        sigma => points[i].sigma;
    }
    
    for(0=>int i; i<N; i++) {
        // Yield every few rows to prevent freeze
        if(i % 5 == 0) GG.nextFrame() => now;
        
        for(0=>int j; j<N; j++) {
            if(i==j) continue;
            distances[i][j] - points[i].rho => float d1; if(d1 < 0) 0 => d1;
            Math.exp(-d1 / points[i].sigma) => float p_ij;
            distances[j][i] - points[j].rho => float d2; if(d2 < 0) 0 => d2;
            Math.exp(-d2 / points[j].sigma) => float p_ji;
            (p_ij + p_ji - (p_ij * p_ji)) => graph[i][j];
        }
    }
}

fun void initialize_layout() {
    for(0=>int i; i<points.size(); i++) {
        Math.random2f(-1, 1) => points[i].x;
        Math.random2f(-1, 1) => points[i].y;
    }
}

fun void run_umap_epoch(int epoch) {
    points.size() => int N;
    (1.0 - (epoch $ float / N_EPOCHS $ float)) * LEARNING_RATE => float alpha;
    if(alpha < 0.001) 0.001 => alpha;
    
    for(0=>int i; i<N; i++) {
        for(0=>int j; j<N; j++) {
            if(i==j || graph[i][j] < 0.01) continue; 
            
            points[i].x - points[j].x => float dx; points[i].y - points[j].y => float dy;
            (dx*dx + dy*dy) => float dist_sq;
            (1.0 / (1.0 + dist_sq)) => float inv_dist;
            graph[i][j] * inv_dist => float force;
            (dx * force * alpha) => float mx; (dy * force * alpha) => float my;
            mx -=> points[i].x; my -=> points[i].y;
            mx +=> points[j].x; my +=> points[j].y;
            
            for(0=>int k; k<NEGATIVE_SAMPLES; k++) {
                Math.random2(0, N-1) => int r;
                if(r == i || r == j) continue;
                points[i].x - points[r].x => float rx; points[i].y - points[r].y => float ry;
                (rx*rx + ry*ry) + 0.001 => float r_dist_sq;
                (1.0 / (0.01 + r_dist_sq)) => float r_force;
                if(r_force > 4.0) 4.0 => r_force; 
                (rx * r_force * alpha * 0.1) => float rmx; (ry * r_force * alpha * 0.1) => float rmy;
                rmx +=> points[i].x; rmy +=> points[i].y;
            }
        }
    }
}

// -----------------------------------------------------------------
// 5. MAIN EXECUTION
// -----------------------------------------------------------------
analyze_audio();
build_fuzzy_graph();
initialize_layout();

spinner.detach(); // Remove Spinner

// Create Real Dots
GSphere dots[points.size()];
FlatMaterial mats[points.size()];

for( 0 => int i; i < points.size(); i++ ) {
    new GSphere @=> dots[i];
    new FlatMaterial @=> mats[i];
    dots[i] --> GG.scene();
    0.3 => dots[i].sca; 
    dots[i].mat( mats[i] );
    points[i].features[0] * 0.5 => float r; 
    points[i].features[2] * 5.0 => float g; 
    mats[i].color( @(r, g, 0.5) );
}

GWindow.title("Authentic UMAP (Interactive)");
int last_played_idx; -1 => last_played_idx;
0 => int current_epoch;

while( true ) {
    if( current_epoch < N_EPOCHS ) {
        run_umap_epoch(current_epoch);
        current_epoch++;
    }

    for( 0 => int i; i < points.size(); i++ ) {
        if(points[i].x > 20) 20 => points[i].x;
        if(points[i].x < -20) -20 => points[i].x;
        if(points[i].y > 20) 20 => points[i].y;
        if(points[i].y < -20) -20 => points[i].y;
        
        points[i].x * 10.0 => float wx;
        points[i].y * 10.0 => float wy;
        dots[i].pos( @(wx, wy, 0) );
    }

    GWindow.mousePos() => vec2 mouse;
    (mouse.x - 512) / 15.0 => float mx;
    (384 - mouse.y) / 15.0 => float my;
    -1 => int hovered_idx; 100.0 => float min_dist;

    for( 0 => int i; i < points.size(); i++ ) {
        dots[i].pos().x => float dx; dots[i].pos().y => float dy;
        Math.hypot(mx - dx, my - dy) => float d;
        if( d < 1.0 && d < min_dist ) { d => min_dist; i => hovered_idx; }
    }

    if( hovered_idx != -1 ) {
        mats[hovered_idx].color( @(1, 1, 1) );
        if( hovered_idx != last_played_idx ) { hovered_idx => last_played_idx; points[hovered_idx].play(); }
    } else { -1 => last_played_idx; }
    
    if(current_epoch % 50 == 0 && current_epoch < N_EPOCHS) <<< "Optimizing...", current_epoch >>>;
    
    GG.nextFrame() => now;
}