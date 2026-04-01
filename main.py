from pipeline.ingestion_pipeline import run_pipeline

if __name__ == "__main__":
    run_pipeline("data/cvs", "output/structured_cvs.json")