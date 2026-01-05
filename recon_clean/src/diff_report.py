import pandas as pd
import argparse
import sys

def generate_diff(old_path, new_path, out_path):
    print(f"Generating diff: {old_path} -> {new_path}")
    
    try:
        df_old = pd.read_csv(old_path)
        df_new = pd.read_csv(new_path)
    except Exception as e:
        print(f"Error reading files: {e}")
        return

    # Normalize cols
    df_old.columns = [c.lower().strip() for c in df_old.columns]
    df_new.columns = [c.lower().strip() for c in df_new.columns]
    
    # We assume 'transaction_ref' or 'ref_no' is key? 
    # Or just row-by-row comparison if index preserved?
    # Broker cleaner preserves rows. Bank parser re-parses so might change row count (merges).
    
    with open(out_path, 'w') as f:
        f.write(f"# Diff Report\n\n")
        f.write(f"Old: {old_path}\n")
        f.write(f"New: {new_path}\n\n")
        f.write(f"Old Row Count: {len(df_old)}\n")
        f.write(f"New Row Count: {len(df_new)}\n\n")
        
        # Sample changes
        f.write("## Sample Changes\n\n")
        
        # If lengths match, side-by-side diff
        if len(df_old) == len(df_new):
            f.write("| Row | Column | Old | New |\n")
            f.write("| --- | --- | --- | --- |\n")
            
            diff_count = 0
            for i in range(len(df_old)):
                if diff_count > 50: break # Limit output
                
                row_o = df_old.iloc[i]
                row_n = df_new.iloc[i]
                
                for col in df_new.columns:
                    val_o = row_o.get(col, '')
                    val_n = row_n.get(col, '')
                    
                    # Fuzzy compare logic (ignore tiny float diff, ignore exact equal)
                    if str(val_o) != str(val_n):
                        f.write(f"| {i} | {col} | {val_o} | {val_n} |\n")
                        diff_count += 1
                        
        else:
            f.write("> **Warning**: Row counts differ. Cannot do direct row-by-row diff.\n\n")
            f.write("### First 10 Rows (New)\n\n")
            # Pandas to markdown
            f.write(df_new.head(10).to_markdown(index=False))

    print(f"Report written to {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--old", required=True)
    parser.add_argument("--new", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    
    generate_diff(args.old, args.new, args.out)
