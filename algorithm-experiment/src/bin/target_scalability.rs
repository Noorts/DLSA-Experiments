use std::{
    fs::File,
    io::Write,
    path::{Path, PathBuf},
    time::Instant,
};

use serde::Serialize;
use sw::{algorithm::find_alignment_simd_lowmem, algorithm::AlignmentScores};

#[derive(Serialize)]
struct Measurements {
    name: String,
    query_size: usize,
    target_size: usize,
    iterations: usize,
    times: Vec<usize>,
}

const WARMUP: usize = 10;
const ITER_PER_SAMPLE: usize = 10;
const SAMPLES: usize = 100;
const QUERY_SIZE: usize = 64 * 5;
const MIN_TARGET_POWER: usize = 10;
const MAX_TARGET_POWER: usize = 20;

type AlignResult = (Vec<char>, Vec<char>, i16, usize, usize);
type AlignFn = fn(&[char], &[char], AlignmentScores) -> AlignResult;

const ALG: AlignFn = find_alignment_simd_lowmem::<64>;

fn main() {
    let platform = std::env::var("PLATFORM").unwrap_or("Local".to_string());
    let result_dir = PathBuf::from("..")
        .join("PC")
        .join(format!(
            "target_scalability-{}",
            sw::get_version().unwrap_or("unknown")
        ))
        .join(platform.clone());

    println!(
        "Running DLSA version: {}",
        sw::get_version().unwrap_or("unknown")
    );
    println!("Platform: {}", platform);
    println!("Writing results to: {}", result_dir.display());

    println!("\nExperiment parameters");
    println!("Warmup iterations: {}", WARMUP);
    println!("Iterations per sample: {}", ITER_PER_SAMPLE);
    println!("Samples: {}", SAMPLES);
    println!("Query size: {}", QUERY_SIZE);
    println!("Minimum target size: {}", 1 << MIN_TARGET_POWER);
    println!("Maximum target size: {}", 1 << MAX_TARGET_POWER);

    let query: Vec<char> = std::iter::repeat('A').take(QUERY_SIZE).collect();

    let scores = AlignmentScores {
        gap: -2,
        r#match: 3,
        miss: -3,
    };

    let target_sizes = (MIN_TARGET_POWER..=MAX_TARGET_POWER)
        .map(|x| 1 << x)
        .collect::<Vec<usize>>();

    for &target_size in &target_sizes {
        let target: Vec<char> = std::iter::repeat('G').take(target_size).collect();
        let measurement = benchmark("Ringbuffer", ALG, &query, &target, scores);
        let path = result_dir.join(format!("{}.json", target_size));

        ensure_directory(&path);

        let mut file = File::create(&path).expect("Could not open result file");
        let data =
            serde_json::to_string(&measurement).expect("Could not convert measurement to json");
        file.write(data.as_bytes())
            .expect("Could not write results");
    }
}

fn ensure_directory<P: AsRef<Path>>(path: P) {
    if let Some(parent) = path.as_ref().parent() {
        std::fs::create_dir_all(parent).expect("Could not create directory");
    }
}

fn benchmark(
    name: &str,
    alignment_function: fn(&[char], &[char], AlignmentScores) -> AlignResult,
    query: &[char],
    target: &[char],
    scores: AlignmentScores,
) -> Measurements {
    let mut times = Vec::new();
    for _ in 0..WARMUP {
        let _ = alignment_function(&query, &target, scores);
    }

    for _ in 0..SAMPLES {
        let start = Instant::now();
        for _ in 0..ITER_PER_SAMPLE {
            let _ = alignment_function(&query, &target, scores);
        }
        let end = Instant::now();
        let duration = (end - start) / ITER_PER_SAMPLE as u32;

        times.push(duration.as_nanos() as usize);
    }

    Measurements {
        name: name.to_string(),
        query_size: query.len(),
        target_size: target.len(),
        iterations: ITER_PER_SAMPLE,
        times,
    }
}
