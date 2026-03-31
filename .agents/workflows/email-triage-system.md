---
description: Email Triage System - How to prioritize, categorize, and route emails using contextual understanding.
---
---
description: Email Triage System - How to prioritize, categorize, and route emails using contextual understanding.
---

### Email Triage System Workflow

This workflow describes how to run and evaluate the Email Triage OpenEnv agent.

1. Install Dependencies
   Run the following command to install the required libraries:
      ```bash
         pip install -r requirements.txt
            ```
            
            2. Start the Environment Server
               Start the FastAPI server that exposes the OpenEnv endpoints:
               // turbo
                  ```bash
                     uvicorn server.app:app --host 0.0.0.0 --port 8000
                        ```
                        
                        3. Run the Baseline Inference Script
                           Execute the inference script to evaluate an agent against the environment. Ensure you have set your environment variables (API_BASE_URL, MODEL_NAME, HF_TOKEN):
                           // turbo
                              ```bash
                                 python inference.py --base-url http://localhost:8000
                                    ```
                                    
                                    4. Verify with Mock Inference (No API Key Required)
                                       Run the mock inference script to verify the environment logic and graders:
                                       // turbo
                                          ```bash
                                             python mock_inference.py
                                                ```
                                                
                                                5. Review Results
                                                   Check inference_results.json for the final scores and server.log for execution details.---
                                                   description: Email Triage System - How to prioritize, categorize, and route emails using contextual understanding.
                                                   ---
                                                   
                                                   ### Email Triage System Workflow
                                                   
                                                   This workflow describes how to run and evaluate the Email Triage OpenEnv agent.
                                                   
                                                   1. **Install Dependencies**
                                                      Run the following command to install the required libraries:
                                                         ```bash
                                                            pip install -r requirements.txt
                                                               ```
                                                               
                                                               2. **Start the Environment Server**
                                                                  Start the FastAPI server that exposes the OpenEnv endpoints:
                                                                  // turbo
                                                                     ```bash
                                                                        uvicorn server.app:app --host 0.0.0.0 --port 8000
                                                                           ```
                                                                           
                                                                           3. **Run the Baseline Inference Script**
                                                                              Execute the inference script to evaluate an agent against the environment. Ensure you have set your environment variables (API_BASE_URL, MODEL_NAME, HF_TOKEN):
                                                                              // turbo
                                                                                 ```bash
                                                                                    python inference.py --base-url http://localhost:8000
                                                                                       ```
                                                                                       
                                                                                       4. **Verify with Mock Inference (No API Key Required)**
                                                                                          Run the mock inference script to verify the environment logic and graders:
                                                                                          // turbo
                                                                                             ```bash
                                                                                                python mock_inference.py
                                                                                                   ```
                                                                                                   
                                                                                                   5. **Review Results**
                                                                                                      Check inference_results.json for the final scores and server.log for execution details.
---
description: Email Triage System - How to prioritize, categorize, and route emails using contextual understanding.
---

### Email Triage System Workflow

This workflow describes how to run and evaluate the Email Triage OpenEnv agent.

1. **Install Dependencies**
   Run the following command to install the required libraries:
      ```bash
         pip install -r requirements.txt
            ```
            
            2. **Start the Environment Server**
               Start the FastAPI server that exposes the OpenEnv endpoints:
               // turbo
                  ```bash
                     uvicorn server.app:app --host 0.0.0.0 --port 8000
                        ```
                        
                        3. **Run the Baseline Inference Script**
                           Execute the inference script to evaluate an agent against the environment. Ensure you have set your environment variables (API_BASE_URL, MODEL_NAME, HF_TOKEN):
                           // turbo
                              ```bash
                                 python inference.py --base-url http://localhost:8000
                                    ```
                                    
                                    4. **Verify with Mock Inference (No API Key Required)**
                                       Run the mock inference script to verify the environment logic and graders:
                                       // turbo
                                          ```bash
                                             python mock_inference.py
                                                ```
                                                
                                                5. **Review Results**
                                                   Check inference_results.json for the final scores and server.log for execution details.
                                                   ### 
