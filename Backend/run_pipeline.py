import time
from teams_extractor import main as run_extractor
from analyze_data import analyze_message_batch as run_analyzer
from calculate_team_metrics import calculate_and_update_team_means as run_metrics

def main():
    print("STARTING DATA UPDATE PIPELINE")
    print("=================================================")
    
    # STEP 1: Extraction
    print("\n[1/3] Extracting data from Microsoft Teams...")
    try:
        run_extractor()
        print("Extraction completed.")
    except Exception as e:
        print(f"Critical error during extraction: {e}")
        return 

    print("\n[2/3] Analyzing sentiment of new messages...")
    try:
        run_analyzer()
        print("Analysis completed.")
    except Exception as e:
        print(f"Error in AI analysis: {e}")
        return 
    print("\n[3/3] Calculating and updating team means...")
    try:
        run_metrics()
        print("Metrics updated in Mongo.")
    except Exception as e:
        print(f"Error calculating means: {e}")
        return

    print("\n=================================================")
    print("SYSTEM UPDATED SUCCESSFULLY")
    print("=================================================")

if __name__ == "__main__":
    main()