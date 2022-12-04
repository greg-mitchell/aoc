(ns aoc.solution2022-3
  (:require [clojure.java.io :as io]
            [clojure.string :as s]
            [clojure.set :as set]))

(def input-file (io/resource "2022/3/input.txt"))
(def input-lines
  (-> input-file
      slurp
      s/split-lines))

(defn parse-rucksack
  [line]
  (let [item-count (count line)
        compartment1 (take (/ item-count 2) line)
        compartment2 (drop (/ item-count 2) line)]
    {:1 compartment1 :2 compartment2}))

(def rucksacks (map parse-rucksack input-lines))

(defn common-items-in-rucksack
  [rucksack]
  (let [compartment1Set (into #{} (:1 rucksack))
        compartment2Set (into #{} (:2 rucksack))
        common (set/intersection compartment1Set compartment2Set)]
    (if (= 1 (count common))
      (first common)
      (throw (Exception. "multiple common items")))))

(def common-items
  (map common-items-in-rucksack rucksacks))

(defn to-priority
  [item]
  (if (= (str item) (s/lower-case item))
    ;; item is lowercase, a-z -> 1-26
    ;; (int \a) => 97
    (- (int item) 96)
    ;; item is uppercase, A-Z -> 27-52
    ;; (int \A) => 65
    (+ (- (int item) 64) 26)))

(def priority-sum
  (->> common-items (map to-priority) (apply +)))

(def groups
  (partition 3 rucksacks))

(defn find-badge
  [rucksacks]
  (let [to-set (fn [rucksack] 
                 (-> #{}
                     (into (:1 rucksack))
                     (into (:2 rucksack))))
        rucksack-sets (map to-set rucksacks)
        badge-set (apply set/intersection rucksack-sets)]
    (if (= 1 (count badge-set))
      (first badge-set)
      (throw (Exception. "multiple badges")))))

(def group-badges
  (map find-badge groups))

(def badge-priority-sum
  (->> group-badges (map to-priority) (apply +)))