pub trait RoutingStrategy {

    fn select(

        &self,

        capability: &str,

    ) -> Option<String>;

}
