import argparse
from utils.bootstrap_helper import BootstrapHelper
from utils.pose_embedding import FullBodyPoseEmbedder
from models.pose_classifier import PoseClassifier
from utils.utils import dump_for_the_app

from inference import predict

def load_bootstrap(bootstrap_helper):
    bootstrap_helper.print_images_in_statistics()
    
    # Bootstrap all images.
    # Set limit to some small number for debug.
    bootstrap_helper.bootstrap(per_pose_class_limit=None)

    # Check how many images were bootstrapped.
    bootstrap_helper.print_images_out_statistics()

    # After initial bootstrapping images without detected poses were still saved in
    # the folderd (but not in the CSVs) for debug purpose. Let's remove them.
    bootstrap_helper.align_images_and_csvs(print_removed_items=False)
    bootstrap_helper.print_images_out_statistics()

def train(args):
    bootstrap_images_in_folder = args.dataset
    bootstrap_images_out_folder = "body"+'_poses_images_out'
    bootstrap_csvs_out_folder = "body"+'_poses_csvs_out'

    bootstrap_helper = BootstrapHelper(
        images_in_folder=bootstrap_images_in_folder,
        images_out_folder=bootstrap_images_out_folder,
        csvs_out_folder=bootstrap_csvs_out_folder,
    )
    load_bootstrap(bootstrap_helper)
    
    # Transforms pose landmarks into embedding.
    pose_embedder = FullBodyPoseEmbedder()

    # Classifies give pose against database of poses.
    pose_classifier = PoseClassifier(
        pose_samples_folder=bootstrap_csvs_out_folder,
        pose_embedder=pose_embedder,
        top_n_by_max_distance=30,
        top_n_by_mean_distance=10)

    outliers = pose_classifier.find_pose_sample_outliers()
    print('Number of outliers: ', len(outliers))

    if args.remove_outlier:
        print("Removing Outlier")
        bootstrap_helper.remove_outliers(outliers)
        bootstrap_helper.align_images_and_csvs(print_removed_items=False)
        bootstrap_helper.print_images_out_statistics()

    dump_for_the_app("body")

def main(args):
    if args.dataset:
        train(args)
    if args.video_path:
        predict(args.video_path, args.result_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-ds","--dataset", help="path to dataset folder") # Required for training
    parser.add_argument("-r","--remove_outlier", help="perform bootstrap", action='store_true')
    parser.add_argument("-v","--video_path", help="video file path") # Required for inference
    parser.add_argument("-res","--result_path", help="video file path", default="results")
    
    args = parser.parse_args()
    main(args)