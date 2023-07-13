# Scripts Execution Order

## src/import

1. Run `scrape_creditfixing.py`
    ```
    python3 scrape_creditfixing.py
    ```

## src/data_wrangling

2. Run `auctions_main_update.py`
    ```
    python3 auctions_main_update.py
    ```

## src/exploration

3. Run `raw_plots_stage1.py`
    ```
    python3 raw_plots_stage1.py
    ```

4. Run `raw_plots_stage2_and_participants.py`
    ```
    python3 raw_plots_stage2_and_participants.py
    ```

## src/data_wrangling

5. Run `unique_dealers_wrangling.py`
    ```
    python3 unique_dealers_wrangling.py
    ```

6. Run `deliverables_xls_csv_individual.py`
    ```
    python3 deliverables_xls_csv_individual.py
    ```

7. Run `deliverable_xls_multiplesheets.py`
    ```
    python3 deliverable_xls_multiplesheets.py
    ```

8. Run `deliverables_xls_senior_sub_2008.py`
    ```
    python3 deliverables_xls_senior_sub_2008.py
    ```

9. Run `deliverables_nanonets.py`
    ```
    python3 deliverables_nanonets.py
    ```

10. Run `deliverables_intermediate_cleaning.py`
    ```
    python3 deliverables_intermediate_cleaning.py
    ```

11. Run `buckets_deliverables.py`
    ```
    python3 buckets_deliverables.py
    ```

12. Run `deliverable_final_cleaning.py`
    ```
    python3 deliverable_final_cleaning.py
    ```

13. Run `auctions_main_deliverables.py`
    ```
    python3 auctions_main_deliverables.py
    ```

## src/exploration

14. Run `summary_statistics.py`
    ```
    python3 summary_statistics.py
    ```
Please ensure to replace `python3` with the correct version of python you're using if different.

