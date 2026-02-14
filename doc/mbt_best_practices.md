# Model-based testing good practises

## 1. Develop model as normal code

Modelling is development work just like coding. Use normal coding good practises like:
* Develop incrementally and iteratively. Create first a tiny model which works and continue
development step by step
* Good code quality. It just make your life easier.


## 2. Modelling level

Most natural model abstraction level and used terminology is the same as system user is using. 
There are multiple reason to do that. 
1. Create model from end user point of view
2. Use user domain level terminology to make able to compare model for user expectations or use cases
3. Right abstraction level helps thinking how system should behave. If model is too complex and not understandable
then maybe real user cannot also understand it. It is normal that modelling raise questions which are not planned 
well enough

## 3. Split model

Split model in logical sub-models. This make code easier to handle big model. This make also able to run different
setups. For example:
* Create a very long test which test just behaviour A
* Create very short test for pull-request test which need to test as much as possible


## 4. Parametrization

Make able to parametrize models to make same model fit in different testing purposes. Examples:
* Functional testing model: Purpose is to check from all possible place after each step that data is correct. No matter 
if model is slow but needed to see the particular action which make data incorrect if it happens.
* Stress test model: Run actions as fast as possible and more likely with multiple branches. Check just that system 
responses. No bit weight for data correctness but need to see if system keep alive
* Reliablity testing: Very long test run which test that data is correct but can also do actions very quickly sometimes.
Purpose is to simulate real usage