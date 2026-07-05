pub trait InferenceProvider {

    fn id(&self) -> &str;

    fn available(&self) -> bool;

    fn infer(

        &self,

        model: &str,

        prompt: &str,

    ) -> Result<String,String>;

}
