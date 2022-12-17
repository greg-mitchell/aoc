(ns aoc.solution2022-4
  (:require [clojure.java.io :as io]
            [clojure.string :as s]))

(def input-file "2022/4/input.txt")
(defn input-lines []
  (-> input-file
      io/resource
      slurp
      s/split-lines))

(defn range->interval
  [range]
  (let [range (s/split range #"-")
        range (map #(Integer/parseInt %) range)
        range (sort range)]
    (vec range)))

(defn line->intervals
  [line]
  (let [intervals (s/split line #",")]
    (if (= 2 (count intervals))
      (->> intervals (map range->interval))
      (throw (Exception. (str "malformed line" line))))))

(defn interval-pairs
  [lines] 
  (map line->intervals lines))

(defn contained?
  [intervals]
  (let [[[lower1 upper1] [lower2 upper2]] (sort intervals)]
    (or 
     ;; i1 and i2 have the same lower, i2 encloses i1
     (and (= lower1 lower2)
          (<= upper1 upper2))
     ;; i1 encloses i2
     (and (>= upper1 lower2)
          (>= upper1 upper2)))))

(defn count-contained
  [interval-pairs]
  (->> interval-pairs
       (map contained?)
       (filter true?)
       count))

#_(def solution1
  (-> (input-lines) interval-pairs count-containedt))

(defn intersect?
  [intervals]
  (let [[[lower1 upper1] [lower2 upper2]] (sort intervals)]
    (<= lower2 upper1)))

(defn count-intersect
  [interval-pairs]
  (->> interval-pairs
       (map intersect?)
       (filter true?)
       count))