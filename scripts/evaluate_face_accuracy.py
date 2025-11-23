import os
import argparse
import cv2
import face_recognition
import numpy as np
from pathlib import Path

def load_images(person_dir, limit=None):
    imgs = []
    files = list(Path(person_dir).glob('*.jpg')) + list(Path(person_dir).glob('*.png'))
    if limit:
        files = files[:limit]
    for f in files:
        img = cv2.imread(str(f))
        if img is None:
            continue
        imgs.append(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    return imgs

def split_train_test(images, ratio=0.7):
    n = len(images)
    if n == 0:
        return [], []
    k = max(1, int(n * ratio))
    return images[:k], images[k:]

def encode_images(images):
    encs = []
    for img in images:
        enc = face_recognition.face_encodings(img)
        if enc:
            encs.append(enc[0])
    return encs

def match_face(known_encs, known_ids, known_names, test_enc, tolerance, margin, model, faces_dir, strict_folder):
    if not known_encs:
        return 'unknown', 'Unknown', 0.0
    dists = face_recognition.face_distance(known_encs, test_enc)
    best_idx = int(np.argmin(dists))
    best_dist = float(dists[best_idx])
    second_best = float(sorted(dists)[1]) if len(dists) > 1 else 1.0
    sep = second_best - best_dist
    cid = known_ids[best_idx]
    if strict_folder and not (Path(faces_dir) / cid).exists():
        return 'unknown', 'Unknown', 0.0
    if best_dist <= tolerance and sep >= margin:
        return cid, known_names[best_idx], max(0.0, 1.0 - best_dist)
    return 'unknown', 'Unknown', 0.0

def evaluate(faces_dir, tolerance, margin, model, limit):
    faces_dir = Path(faces_dir)
    persons = [d for d in faces_dir.iterdir() if d.is_dir()]
    per_person = {}
    overall_correct = 0
    overall_total = 0
    for p in persons:
        name = p.name
        imgs = load_images(p, limit)
        train, test = split_train_test(imgs)
        known_encs = encode_images(train)
        known_ids = [name] * len(known_encs)
        known_names = [name] * len(known_encs)
        correct = 0
        total = 0
        for timg in test:
            enc = face_recognition.face_encodings(timg)
            if not enc:
                continue
            pid, pname, conf = match_face(known_encs, known_ids, known_names, enc[0], tolerance, margin, model, faces_dir, True)
            total += 1
            if pid == name:
                correct += 1
        per_person[name] = {'correct': correct, 'total': total, 'accuracy': (correct / total) if total else 0.0}
        overall_correct += correct
        overall_total += total
    return per_person, overall_correct, overall_total

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--faces-dir', default=str(Path(__file__).resolve().parents[1] / 'data' / 'faces'))
    parser.add_argument('--tolerance', type=float, default=0.6)
    parser.add_argument('--margin', type=float, default=0.06)
    parser.add_argument('--model', default='hog')
    parser.add_argument('--limit', type=int, default=None)
    args = parser.parse_args()
    per_person, ok, tot = evaluate(args.faces_dir, args.tolerance, args.margin, args.model, args.limit)
    print('Person,Correct,Total,Accuracy')
    for k, v in per_person.items():
        print(f"{k},{v['correct']},{v['total']},{v['accuracy']:.2f}")
    acc = (ok / tot) if tot else 0.0
    print(f'Overall,{ok},{tot},{acc:.2f}')

if __name__ == '__main__':
    main()