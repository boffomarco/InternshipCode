# Import libraries
import pykeen

def rm_main():

	config = dict(
	    training_set_path           = '%{FolderPath}/%{DatasetFinalName}.tsv',
	    execution_mode              = '%{execution_mode}',
	    kg_embedding_model_name     = '%{kg_embedding_model_name}',
	    embedding_dim               = %{embedding_dim},
	    normalization_of_entities   = %{normalization_of_entities},  # corresponds to L2
	    scoring_function            = %{scoring_function},  # corresponds to L1
	    margin_loss                 = %{margin_loss},
	    learning_rate               = %{learning_rate},
	    batch_size                  = %{batch_size},
	    num_epochs                  = %{num_epochs},
	    test_set_ratio              = %{test_set_ratio},
	    filter_negative_triples     = %{filter_negative_triples},
	    random_seed                 = %{random_seed},
	    preferred_device            = '%{preferred_device}',
	    maximum_number_of_hpo_iters = %{maximum_number_of_hpo_iters},
	)

	results = pykeen.run(
	    config=config,
	    output_directory="%{ResultDirectory}",
	)

	# Create output files
	with open(r"%{ResultDirectory}/%{DatasetFinalName}_trained_model.txt", "w+") as res:
		res.write(str(results.trained_model)+"\n")

	# Create output files
	with  open(r"%{ResultDirectory}/%{DatasetFinalName}_losses.txt", "w+") as res:
		res.write(str(results.losses)+"\n") 	

	# Create output files
	with open(r"%{ResultDirectory}/%{DatasetFinalName}_evaluation_summary.txt", "w+") as res:
		res.write(str(results.evaluation_summary)+"\n") 	