# Overview: 
This homework assignment connects two important concepts you have learned this semester: 
knowledge representation and machine learning. You will also be working with ideas that are not 
described in your textbook, as this is cutting-edge research. For this reason, I am allowing you to 
form teams of up to three people. If you choose to form a team, you must send an email to me by 
11pm on Monday, April 20, identifying and cc’ing all of your teammates. 
Like the previous practical homework, you will be able to do all of this using a Jupyter notebook. 
However, some of the steps in this homework will take over an hour to run, so rather than use 
Google Colab, we have created a GPU environment hosted on Lehigh’s MAGIC machines for 
you to use. You can access this environment via a web browser: http://magic01.cse.lehigh.edu/ . 
Details on using the environment are here: https://docs.cse.lehigh.edu/magic/ . If you formed a 
team, you will want to be careful about coordinating any code changes you make. I strongly 
recommend using BitBucket or GitHub, but if you divide the work in a way that avoids having 
multiple people changing the same file at the same time, you may not need these tools.  

# Submission: 
Make a ZIP file that contains your source (.py) and any supporting files. For each KB you create, 
you should include a subdirectory with all of the files that were produced, including the KB 
itself, any loss diagrams (.png files), and the `vocab.pkl`, `all_facts.txt`, `train_queries.txt`, 
`test_queries.txt`, and `mr_train_examples.csv` files. Use Google Docs or a word processor to 
record the commands you executed, the resulting output (the first and last 20 lines are fine for 
output that is over 50 lines long) and answer any questions below. Make sure the top of this file 
identifies the names and emails of all your teammates. Save this as a PDF. 
## Exercises: 
1. Login to the MAGIC environment and upload the files I have provided. You can use unzip if 
you uploaded the zipped file. If you want to run commands in a MAGIC terminal, then issue 
`conda activate cse327python311` first to select the correct Python environment. 
2. Open the `CSE 327 P4.jpynb` Jupyter notebook. Select Kernel→ Change Kernel… and choose 
`cse327python311` from the dropdown list. Read through the notebook and run all of the code 
blocks. Note, if you want to run the examples in a local Python environment (or in the 
MAGIC terminal), you should remove the “%” and “!” from the front of commands. You do 
not need to include any results from this exercise in your final document. 
3. Select a topic area that you are interested in. Create a knowledge base (KB) that models the 
topic as best you can within the limitations of Datalog. Your KB must have at least 300 
statements, including at least 30 rules. It must be possible to infer at least 100 new facts from 
the KB, at least 10 of which have a depth of 3 or greater. You can test the KB for these 
properties by running the `python kbencoder.py -g` command. Note, Datalog is just an 
alternate syntax for the Horn logic KBs we used with backward and forward-chaining in 
class. It uses the same syntax as Prolog (see pp. 294-295), but without the list notation. 
Warning: In Datalog, anything that starts with a capital letter is treated as a variable. Be sure 
to use leading lowercase letters for all constants, even those that are proper nouns. 
4. Following the steps of the demo in Ex. 1, train an embedding and scoring model on your KB. 
Use the test queries to compare the scoring model to the standard backward-chaining 
reasoner. Which performed better? Look at the detailed query results. Are there specific 
types of queries where one reasoner did significantly better than the other? 
5. Use the code to generate three random KBs of sizes 200, 300, and 400. To keep from 
overwriting important files, it is recommended that you create each in its own subdirectory. 
For example, if you want to put the 400 statement KB in a directory named size400: 
```bash
cd size400 
python ..\kbencoder.py --generate_kb --num_rules 400 --new_vocab --save_vocab 
```
6. For each random KB, train the embedding and scoring models and then compare reasoning 
using the scoring model to the standard reasoner. 
7. By default, the system uses an embedding size of 50, meaning that the meaning of every 
atom is represented by a 50-dimensional vector of numbers. Select a different embedding 
size and train a new embedding model and scoring model for your custom KB as well as 
each of your random KBs. To specify an embedding size, you can add the `--embed_size` 
argument when running `kbencoder` with the train_unification_model option. The same 
option (with the same value) should be used when running `nnreasoner` and. To avoid 
overwriting your `rKB_model.pth` file, use `--embed_model_path` to specify and use an 
alternate name when running `kbencoder`, `nnreasoner`, and `evaluate`. To avoid overwriting 
your `uni_mr_model.pt` file, use `--save_model` with `nnreasoner` and `--scoring_model_path` 
with evaluate. You can (and should) use the same `vocab.pkl`, `mr_train_examples.csv`, and 
`test_queries.txt` that you used in the previous steps. Assuming you have run the code for each 
KB in a separate directory, you do not need to rerun any other steps than the two training 
steps and the evaluation. Does your new embedding size lead to a better or worse training 
loss for the embedding and scoring model? Does it improve or worsen performance on the 
test queries? Why do you think this is? 
8. The architecture (layers, activation functions, etc.) of the scoring model are defined in the 
NeuralNet class of `nnreasoner.py`. Change this architecture in some interesting way that 
you think might lead to improved performance on answering queries. Note, when 
``evaluate.py`` uses the scoring model, it creates an instance of the NeuralNet class, and then 
loads the learned parameters from a file (see `load_guidance()`). If you create a new class for 
your modified model, you’ll need to write some code to load it properly.  
9. Train and evaluate your modified model on all four KBs. 
10. Create a table that summarizes the results of your experiments. For each combination of KB 
(your custom one plus the three random) and test condition (standard, default scoring model, 
scoring model with new embedding size (from Ex. 6), modified model (from Ex. 7 and 8), it 
should display the mean and median nodes explored to answer the test queries. 
11. In your document, reflect on what you have learned through these experiments. Which 
versions of the learned model worked best? What sorts of differences do you see in 
performance across different KBs?  