from collections import OrderedDict
from nnunet.paths import nnUNet_raw_data
from batchgenerators.utilities.file_and_folder_operations import *
import shutil
import argparse
from sklearn.model_selection import train_test_split

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-dataset_path", type=str,
                        default='/home/lwt/data_pro/flare')
    args = parser.parse_args()

    task_id = 160
    task_name = "ACTF"
    foldername = "Task%03.0d_%s" % (task_id, task_name)

    out_base = join(nnUNet_raw_data, foldername)
    imagestr = join(out_base, "imagesTr")
    imagests = join(out_base, "imagesTs")
    labelstr = join(out_base, "labelsTr")
    labelsts = join(out_base, "labelsTs")
    if isdir(imagestr):
        shutil.rmtree(imagestr)
        shutil.rmtree(imagests)
        shutil.rmtree(labelstr)
        shutil.rmtree(labelsts)

    maybe_mkdir_p(imagestr)
    maybe_mkdir_p(imagests)
    maybe_mkdir_p(labelstr)
    maybe_mkdir_p(labelsts)

    train_image_folder = join(args.dataset_path, "Subtask1/Subtask1/TrainImage")
    train_label_folder = join(args.dataset_path, "Subtask1/Subtask1/TrainMask")
    test_image_folder = join(args.dataset_path, "TestImage/TestImage")

   
    train_image = subfiles(train_image_folder, join=False, suffix='nii.gz')
    train_label = subfiles(train_label_folder, join=False, suffix='nii.gz')
    test_image = subfiles(test_image_folder, join=False, suffix='nii.gz')
    train_names = []
    test_names = []
    for i in train_image:
        train_name = f'{task_name}_{int(i[6:10]):04d}.nii.gz'
        # a = f'{train_name[:-7]}_0000.nii.gz'
        shutil.copy(join(train_image_folder, i), join(imagestr, f'{train_name[:-7]}_0000.nii.gz'))
        shutil.copy(join(train_label_folder, f"{i[:-12]}.nii.gz"), join(labelstr, train_name))
        train_names.append(train_name)
    for i in test_image:
        test_name = f'{task_name}_{int(i[5:9]):04d}.nii.gz'
        shutil.copy(join(test_image_folder, i), join(imagests, test_name))
        test_names.append(test_name)
    json_dict = OrderedDict()
    json_dict['name'] = "AbdomenCT-1KFullySupervisedLearningBenchmark"
    json_dict['description'] = "AbdomenCT-1K: Fully Supervised Learning Benchmark"
    json_dict['tensorImageSize'] = "3D"
    json_dict['reference'] = "https://zenodo.org/record/5903037#.YlQh65pBxhG"
    json_dict['licence'] = "see challenge website"
    json_dict['release'] = "0.0"
    json_dict['modality'] = {
        "0": "CT",
    }
    json_dict['labels'] = OrderedDict({
        "00": "background",
        "01": "liver",
        "02": "kidney",
        "03": "spleen",
        "04": "pancreas"
        }
    )
    json_dict['numTraining'] = len(train_image)
    json_dict['numTest'] = len(test_image)

    json_dict['test'] = ["./imagesTs/%s" % i for i in test_names]

    json_dict['training'] = [{'image': "./imagesTr/%s" % i,
                              "label": "./labelsTr/%s" % i} for i in train_names]

    save_json(json_dict, os.path.join(out_base, "dataset.json"))

    train, val, _, _ = train_test_split(train_names, train_names, test_size=0.2, random_state=42)
    splits = []
    splits.append(OrderedDict())
    # splits[-1]['train'] = [i[:7]
    #                        for i in train_patient_names if int(i[4:7]) not in val_id]
    # splits[-1]['val'] = [i[:7]
    #                      for i in train_patient_names if int(i[4:7]) in val_id]
    # save_pickle(splits, join(out_base, "splits_final.pkl"))
    splits[-1]['train'] = [i.split(".")[0]
                           for i in train]
    splits[-1]['val'] = [i.split(".")[0]
                           for i in val]
    save_pickle(splits, join(out_base, "splits_final.pkl"))


if __name__ == "__main__":
   main()

    