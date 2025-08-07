import re
import os
import time
import datetime
import configparser as cp

from zoxide import ZoxideDB

config = cp.ConfigParser()
config.read("config.ini")

class Populator:
    """
    Class to populate the Zoxide database by traversing a directory tree.
    """

    @staticmethod
    def populate_by_traversing(db: ZoxideDB, root, regex_keep=None, regex_discard=None):
        """
        Populate the database by traversing a directory tree.

        Parameters
        ----------
        root : str
            Root directory to start traversing.
        """
        for dirpath, _, _ in os.walk(root):
            if regex_keep:
                if not re.search(regex_keep, dirpath):
                    continue
            if regex_discard:
                if re.search(regex_discard, dirpath):
                    continue
            db.add(dirpath)
            
    @staticmethod
    def populate_by_gemini(db: ZoxideDB, root):
        """
        Populate the database using the Gemini API.
        https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models?hl=it#gemini-models

        Parameters
        ----------
        db : ZoxideDB
            The database to populate.
        root : str
            Root directory to start traversing.
        """
        from google import genai
        from google.genai import types
        
        base_prompt = """
You are an expert at identifying relevant file system paths. You will be provided with a path, and you must decide whether it is a "relevant" path that a user is likely to visit frequently or an "irrelevant" system or temporary path that should be discarded.

Your task is to respond with a single word: `keep` or `discard`.

**Example:**

Paths: E:\\Users\\laura, C:\\Users\\laura\\Documents\\Projects, Q:\\Users\\despo\\Desktop\\SJQ\\wetransfer_giudice-e-oyo_2025-02-19_0142, A:\\Users\\despo\\Desktop\\STL, F:\\Windows\\WinSxS\\amd64_microsoft-windows-w..sh-helper.resources_31bf3856ad364e35_10.0.26100.4484_it-it_2573d45031c5f331, H:\\MinGW\\include\\glbinding\\gl42, B:\\Windows\\WinSxS\\wow64_microsoft-windows-directshow-core_31bf3856ad364e35_10.0.26100.1_none_adb88a938ad3880c, R:\\Windows\\apppatch\\MergeSdbFilesSource, S:\\Users\\despo\\Zotero\\storage\\83IWMEUH, T:\\$Recycle.Bin\\S-1-5-21-3277155917-2146125615-2778160253-1001\\$RKDGAWT\\.git\\logs, D:\\MinGW\\git\\mingw64\\ssl, M:\\Users\\despo\\.x2go, L:\\Users\\despo\\Documents\\moore
Answers: keep,keep,keep,keep,discard,discard,discard,discard,discard,discard,discard,discard,keep

The actual paths are: 
"""

        # export the API key as an environment variable
        os.environ["GEMINI_API_KEY"] = config.get("POPULATOR", "gemini_api_key")
        client: genai.Client = genai.Client()

        max_input_tokens = 1000000 // 10 # 10 % of the max input tokens
        max_batch_size = 30  # Maximum number of paths per batch
        rate_min_rpm = 30
        rate_day_rpd = 200
        seconds_per_request = 60.0 / rate_min_rpm
        
        print(f"Walking '{root}' to find all subdirectories...")
        all_folders = []
        for dirpath, _, _ in os.walk(root):
            all_folders.append(dirpath)
        
        if not all_folders:
            print("No folders found in the specified root directory.")
            return

        print(f"Found {len(all_folders)} folders to process.")
        
        prompts = []
        current_batch = []

        for folder_path in all_folders:
            # Construct a potential prompt to test its token count.
            test_content = ",".join(current_batch + [folder_path])
            test_prompt = f"{base_prompt} {test_content}"

            # # Get the token count for the new prompt.
            # try:
            #     token_count = client.models.count_tokens(
            #         model=config.get("POPULATOR", "gemini_model"),
            #         contents=test_prompt
            #     ).total_tokens
            # except Exception as e:
            #     print(f"Error counting tokens for a prompt: {e}. Skipping folder: {folder_path}")
            #     continue
            token_count = len(test_prompt)  # Simplified token count for demonstration

            if token_count > max_input_tokens or len(current_batch) >= max_batch_size:
                # If adding this folder exceeds the limit, save the current batch
                # and start a new one with the current folder.
                if current_batch:
                    prompts.append(",".join(current_batch))
                    current_batch = [folder_path]
            else:
                current_batch.append(folder_path)
        
        # Add any remaining paths in the last batch
        if current_batch:
            prompts.append(", ".join(current_batch))

        print(f"Divided all folders into {len(prompts)} batches based on token limits.")
        # print("Batches lengths: ", [len(batch.split(", ")) for batch in prompts])
        
        with open("gemini_response.gemlog", "a") as f:
            for i, path_batch in enumerate(prompts):
                batch_paths = path_batch.split(",")
                full_prompt = f"{base_prompt} {path_batch}"
                print(f"Processing batch {i + 1}, npaths={len(batch_paths)}...")

                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash", 
                        contents=full_prompt,
                        config=types.GenerateContentConfig(
                            thinking_config=types.ThinkingConfig(thinking_budget=0) # Disables thinking
                        ))
                    
                    print(f"Response for batch {i + 1}: {response.text}\n")
                    
                    # Reply date - time
                    f.write(f"\n\nReply of {datetime.datetime.now()}\n\n")
                    # print the batch in the first column and the response in the second column
                    responses = response.text.split(",")
                    for i in range(len(responses)):
                        f.write(f"{batch_paths[i].strip()}\t{responses[i].strip()}\n")
                    
                    # db.add_entry(path=path_batch, ai_summary=ai_summary)
                    print(f"Successfully processed batch {i + 1}.")
                except Exception as e:
                    print(f"API call failed for batch {i + 1}: {e}")
                
                # Pause to respect the rate limit
                if i < len(prompts) - 1:
                    print(f"Waiting for {seconds_per_request:.2f} seconds to adhere to rate limit.")
                    time.sleep(seconds_per_request)
                    
                if i == 3: break  # DEBUG

        print("Gemini database population complete.")
           

if __name__ == "__main__":
    import configparser as cp
    
    config = cp.ConfigParser()
    config.read("config.ini")
    db = ZoxideDB(config, "zoxide_test_db.json")
    # Populator.populate_by_traversing(db, "/path/to/start", regex_keep=r"keep_pattern", regex_discard=r"discard_pattern")
    
    Populator.populate_by_gemini(db, "C:\\Users\\l.ribotta\\Documents")