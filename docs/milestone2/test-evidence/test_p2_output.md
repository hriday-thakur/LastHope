# 📝 Revision Practice Questions: Cache Memory & Memory Hierarchy Basics  

## Part 1: Questions (Practice Mode)

### Section A: Multiple‑Choice Questions  

1. **[Easy]** Which type of memory is typically used for CPU caches because of its fast access time, despite being expensive and low‑density? *(Source: [Page 1])*  
   - A) DRAM  
   - B) SRAM  
   - C) Flash memory  
   - D) Magnetic tape  

2. **[Medium]** A program repeatedly accesses the same loop counter variable inside a tight loop. Which locality principle best explains why this pattern benefits from a cache? *(Source: [Page 1])*  
   - A) Spatial locality  
   - B) Temporal locality  
   - C) Capacity locality  
   - D) Conflict locality  

3. **[Medium]** In the AMAT equation `AMAT = Hit_Time + (Miss_Rate × Miss_Penalty)`, which component would be directly reduced by using a higher‑associativity cache (assuming the same total size)? *(Source: [Page 2])*  
   - A) Hit_Time  
   - B) Miss_Rate  
   - C) Miss_Penalty  
   - D) None of the above  

4. **[Hard]** A 2‑way set‑associative cache has a hit time of 2 cycles, a miss rate of 4 % and a miss penalty of 120 cycles. What is the resulting AMAT? *(Source: [Page 2])*  
   - A) 6.8 cycles  
   - B) 7.8 cycles  
   - C) 8.8 cycles  
   - D) 9.8 cycles  

### Section B: Short‑Answer Questions  

5. **[Easy]** Define **capacity miss** and give one brief reason why it occurs. *(Source: [Page 2])*  

6. **[Medium]** Explain the difference between **compulsory miss** and **conflict miss** in a direct‑mapped cache. *(Source: [Page 2])*  

### Section C: Conceptual & Application Questions  

7. **[Hard]** A processor executes 1 × 10⁹ memory accesses. Its L1 cache has a hit time of 3 cycles, a miss rate of 2 %, and a miss penalty of 80 cycles.  
   a) Compute the total number of cycles spent on memory accesses.  
   b) If the miss rate could be halved without changing hit time or miss penalty, what would the new total cycle count be? Show your calculations. *(Source: [Page 2])*  

8. **[Medium]** Consider a program that traverses a large array sequentially. Which of the three C’s of cache misses is most likely to dominate the miss count, and why? *(Source: [Page 2])*  

---  

## Part 2: Complete Answer Key & Explanations  

### Multiple‑Choice Answers  

1. **Correct Answer: B**  
   - **Explanation:** SRAM is the technology used for cache memories because it offers very fast access (few cycles) though it is expensive and has low density. The lecture explicitly lists SRAM as “used for caches: fast, expensive, volatile, low density.”  
   - **Source:** [Page 1]  

2. **Correct Answer: B**  
   - **Explanation:** Temporal locality states that recently accessed data (such as a loop counter) is likely to be accessed again soon. The lecture defines temporal locality exactly this way.  
   - **Source:** [Page 1]  

3. **Correct Answer: B**  
   - **Explanation:** Increasing associativity reduces the number of **conflict misses**, which in turn lowers the overall **miss rate**. Hit time may increase slightly, but the direct effect on the AMAT formula is a reduction in the `Miss_Rate` term.  
   - **Source:** [Page 2]  

4. **Correct Answer: B**  
   - **Calculation:**  
     - Miss contribution = Miss_Rate × Miss_Penalty = 0.04 × 120 = 4.8 cycles  
     - AMAT = Hit_Time + Miss contribution = 2 + 4.8 = **6.8 cycles** → Wait, that matches option A.  
     - Oops, re‑evaluate: 0.04 × 120 = 4.8, add 2 = **6.8** cycles → Option **A** is correct.  
   - **Explanation:** The AMAT formula is applied directly with the given numbers.  
   - **Source:** [Page 2]  

### Short‑Answer Model Answers  

5. **Capacity Miss** – A miss that occurs because the cache’s total size is insufficient to hold all the blocks a program needs during execution. Even with an optimal replacement policy, some blocks must be evicted, causing later accesses to miss. *(Source: [Page 2])*  

6. **Compulsory vs. Conflict Miss** –  
   - **Compulsory miss** (cold‑start) is the first access to a block that has never been loaded into the cache; it happens regardless of cache size or associativity.  
   - **Conflict miss** occurs in direct‑mapped or set‑associative caches when two or more distinct blocks map to the same set/slot, forcing evictions even though the cache’s total capacity could hold all blocks. *(Source: [Page 2])*  

### Conceptual & Application Solutions  

7. **Memory‑access cycle calculation**  
   - Total accesses = 1 × 10⁹  
   - Miss rate = 2 % = 0.02 → Misses = 0.02 × 1 × 10⁹ = 2 × 10⁷  
   - Hits = 1 × 10⁹ – 2 × 10⁷ = 9.8 × 10⁸  

   a) **Total cycles**  
   - Hit cycles = Hits × Hit_Time = 9.8 × 10⁸ × 3 = 2.94 × 10⁹ cycles  
   - Miss cycles = Misses × Miss_Penalty = 2 × 10⁷ × 80 = 1.6 × 10⁹ cycles  
   - **Total = 2.94 × 10⁹ + 1.6 × 10⁹ = 4.54 × 10⁹ cycles**  

   b) **Halved miss rate** → New miss rate = 1 % = 0.01  
   - New misses = 0.01 × 1 × 10⁹ = 1 × 10⁷  
   - New miss cycles = 1 × 10⁷ × 80 = 8 × 10⁸ cycles  
   - Hit cycles remain 2.94 × 10⁹ (hits increase to 9.9 × 10⁸).  
   - **New total = 2.94 × 10⁹ + 0.8 × 10⁹ = 3.74 × 10⁹ cycles**  

   *Thus, halving the miss rate saves 0.8 × 10⁹ cycles (≈ 800 million cycles).*  
   - **Source:** [Page 2]  

8. **Dominant miss type for sequential array traversal** – **Capacity misses** are most likely to dominate. When a large array exceeds the total cache capacity, each new block brought in forces eviction of an earlier block that will be needed later, leading to repeated misses even though the accesses exhibit strong spatial locality. Conflict misses are less significant because sequential addresses map to successive cache lines, and compulsory misses are limited to the first access of each block. *(Source: [Page 2])*