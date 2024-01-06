use std::{
    fs::File,
    io::Write,
    path::{Path, PathBuf},
    time::Instant,
};

use rand::{distributions::Uniform, Rng};
use serde::Serialize;
use sw::{
    algorithm::find_alignment_simd_lowmem, algorithm::AlignmentScores,
    find_alignment_sequential_straight, find_alignment_simd,
};

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
const TARGET_SIZE: usize = 1024 * 32;

type AlignResult = (Vec<char>, Vec<char>, i16, usize, usize);
type AlignFn = fn(&[char], &[char], AlignmentScores) -> AlignResult;

const NEUCLEOTIDES: [char; 4] = ['A', 'C', 'G', 'T'];

fn main() {
    let platform = std::env::var("PLATFORM").unwrap_or("Local".to_string());
    let result_dir = PathBuf::from("..")
        .join(platform.to_uppercase())
        .join(format!(
            "algorithm_{}",
            sw::get_version().unwrap_or("unknown")
        ));

    println!("Running DLSA version: {}", sw::get_version().unwrap_or("unknown"));
    println!("Platform: {}", platform);
    println!("Writing results to: {}", result_dir.display());

    println!("\nExperiment parameters");
    println!("Warmup iterations: {}", WARMUP);
    println!("Iterations per sample: {}", ITER_PER_SAMPLE);
    println!("Samples: {}", SAMPLES);
    println!("Query size: {}", QUERY_SIZE);
    println!("Target size: {}", TARGET_SIZE);

    let query: Vec<char> = std::iter::repeat('A').take(QUERY_SIZE).collect();

    let target_disjoint: Vec<char> = std::iter::repeat('G').take(TARGET_SIZE).collect();
    let target_equal: Vec<char> = std::iter::repeat('A').take(TARGET_SIZE).collect();

    let target_random: Vec<char> = rand::thread_rng()
        .sample_iter(Uniform::from(1..4))
        .map(|x| NEUCLEOTIDES[x])
        .take(TARGET_SIZE)
        .collect();

    let targets = [
        ("equal", target_equal.clone()),
        ("disjoint", target_disjoint.clone()),
        ("random", target_random.clone()),
    ];

    let scores = AlignmentScores {
        gap: -2,
        r#match: 3,
        miss: -3,
    };

    let algs: Vec<(String, AlignFn)> = vec![
        (String::from("01"), find_alignment_simd_lowmem::<01>),
        (String::from("02"), find_alignment_simd_lowmem::<02>),
        (String::from("04"), find_alignment_simd_lowmem::<04>),
        (String::from("08"), find_alignment_simd_lowmem::<08>),
        (String::from("16"), find_alignment_simd_lowmem::<16>),
        (String::from("32"), find_alignment_simd_lowmem::<32>),
        (String::from("64"), find_alignment_simd_lowmem::<64>),
    ];

    for (target_name, target) in &targets {
        for (name, alg) in &algs {
            let measurement = benchmark(name, *alg, &query, &target, scores);
            let path = result_dir.join(format!("simd_lanes_ringbuf/{}/{}.json", target_name, name));

            ensure_directory(&path);

            let mut file = File::create(&path).expect("Could not open result file");
            let data =
                serde_json::to_string(&measurement).expect("Could not convert measurement to json");
            file.write(data.as_bytes())
                .expect("Could not write results");
        }
    }

    let algs: Vec<(String, AlignFn)> = vec![
        (String::from("01"), find_alignment_simd::<01>),
        (String::from("02"), find_alignment_simd::<02>),
        (String::from("04"), find_alignment_simd::<04>),
        (String::from("08"), find_alignment_simd::<08>),
        (String::from("16"), find_alignment_simd::<16>),
        (String::from("32"), find_alignment_simd::<32>),
        (String::from("64"), find_alignment_simd::<64>),
    ];

    for (target_name, target) in &targets {
        for (name, alg) in &algs {
            let measurement = benchmark(name, *alg, &query, &target, scores);
            let path = result_dir.join(format!("simd_lanes/{target_name}/{}.json", name));
            ensure_directory(&path);
            let mut file = File::create(&path).expect("Could not open result file");
            let data =
                serde_json::to_string(&measurement).expect("Could not convert measurement to json");
            file.write(data.as_bytes())
                .expect("Could not write results");
        }
    }

    // Sequential
    let measurement = benchmark(
        "Sequential",
        find_alignment_sequential_straight,
        &query,
        &target_equal,
        scores,
    );
    let path = result_dir.join("sequential.json");
    ensure_directory(&path);
    let mut file = File::create(&path).expect("Could not open result file");
    let data = serde_json::to_string(&measurement).expect("Could not convert measurement to json");
    file.write(data.as_bytes())
        .expect("Could not write results");
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
