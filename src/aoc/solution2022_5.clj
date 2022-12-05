(ns aoc.solution2022-5
  (:require [clojure.java.io :as io]
            [clojure.string :as s]))

(def input-file (io/resource "2022/5/input.txt"))
(def input-lines
  (-> input-file
      slurp
      s/split-lines))

(defn find-stacks-line
  "finds the line like: 
   1   2   3   4   5   6   7   8   9 "
  [lines]
  (let [indexed-lines (map-indexed (fn [idx line] [idx line]) lines)
        indexed-stack-line (filter #(s/starts-with? (second %) " 1") indexed-lines)]
    (if (= 1 (count indexed-stack-line))
      (first indexed-stack-line)
      (throw (Exception. "multiple stack sections")))))

(defn parse-stack-count
  [[_idx stacks-line]]
  (-> stacks-line
      (s/split #"\s+")
      last
      (Integer/parseInt)))

(def stack-info
  "number of stacks there are and problem metadata"
  (let [stack-line (find-stacks-line input-lines)]
    {:stack-count (parse-stack-count stack-line)
     :max-depth (first stack-line)}))

(defn build-stacks
  [{:keys [stack-count max-depth]} input-lines]
  (let [;; splits each line by stack, either the Box char or space (no box)
        splitter (fn [line] (into [] (map second (partition 3 4 line))))
        split-lines (into [] (map splitter (take max-depth input-lines)))
        stacks (map (fn [stack-i]
                      (->> split-lines
                           (map (fn [line] (nth line stack-i)))
                           (filter #(not (= % \space)))
                           reverse
                           (into [])))
                    (range stack-count))]
    (into [] stacks)))

(def stacks
  (build-stacks stack-info input-lines))

(def procedure-lines
  (drop (+ 2 (:max-depth stack-info)) input-lines))

(defn parse-procedure-steps
  [line]
  (let [matches (re-find #"move (\d+) from (\d+) to (\d+)" line)
        matches (map #(Integer/parseInt %) (drop 1 matches))]
    (if (empty? matches)
      (throw (Exception. (str "invalid procedure line" line)))
      {:move-count (nth matches 0)
       :from (nth matches 1)
       :to (nth matches 2)})))

(def procedure
  (map parse-procedure-steps procedure-lines))

(defn apply-step
  [stacks {:keys [move-count from to]}]
  (let [from (dec from)
        to (dec to)]
    (loop [result-stacks stacks
           to-move move-count]
    ;; move one item
      (if (= 0 to-move)
        result-stacks 
        (let [from-stack (nth result-stacks from)
              item (peek from-stack)
              from-stack (pop from-stack)
              to-stack (conj (nth result-stacks to) item)
              ;_ (println "from-stack" from-stack "to-stack" to-stack)
              with-updated-from (assoc-in result-stacks [from] from-stack)
              updated-stack (assoc-in with-updated-from [to] to-stack)]
          ;(println "Updated stack" updated-stack)
          (recur
           updated-stack
           (dec to-move)))))))

(defn apply-procedure
  [step-fn initial-stacks procedure]
  (loop [stacks initial-stacks
         steps procedure]
    (if (empty? steps)
      stacks
      (recur (step-fn stacks (first steps))
             (rest steps)))))

(def final-stacks
  (apply-procedure apply-step stacks procedure))

(def tops
  (->> final-stacks
       (map last)
       (apply str)))

;; part 2

(defn apply-step2
  [stacks {:keys [move-count from to]}]
  (let [from (dec from)
        to (dec to)
        from-stack (nth stacks from)
        remaining-item-count (- (count from-stack) move-count)
        _ (println remaining-item-count)
        items (drop remaining-item-count from-stack)
        from-stack (take remaining-item-count from-stack)
        to-stack (concat (nth stacks to) items)
        _ (println "items" items "from" from-stack "to" to-stack)
        with-updated-from (assoc-in stacks [from] from-stack)
        updated-stack (assoc-in with-updated-from [to] to-stack)]
    updated-stack))

(def final-stacks2
  (apply-procedure apply-step2 stacks procedure))

(def tops2
  (->> final-stacks2
       (map last)
       (apply str)))